import tk_ as tk
import tkinter.messagebox as tkmb
import config
from PIL import ImageTk
from tooltip import ToolTip
import re

it = config.ItemTypes()
msg = config.Messages()


class ItemEditor(tk.Toplevel):
    def __init__(self, app, item):
        tk.Toplevel.__init__(self)
        self.style = app.style
        self.app = app
        self.char = app.char
        self.item = item
        self.widgets = {}

        self.item_name = item.get("name")
        self.item_quantity = int(item.get("quantity", "1"))
        self.item_price = float(item.get("price", "0"))
        self.item_quality = int(item.get("quality","6"))

        self.description_content = ""

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.item_screen = tk.Frame(self)
        self.item_title = tk.Frame(self.item_screen)
        self.item_body = tk.Frame(self.item_screen)
        self.item_title.pack(fill=tk.X, expand=1, anchor=tk.N)
        self.item_body.pack(fill=tk.BOTH, expand=1, anchor=tk.N)
        self.item_menu = tk.Frame(self)
        self.item_screen.pack(
            fill=tk.BOTH,
            expand=1,
            anchor=tk.NW
        )
        self.item_menu.pack(side=tk.BOTTOM, anchor=tk.SW, fill=tk.X)
        self.setMinHeight()
 
        # important variables:
        self.split_number = tk.IntVar()
        self.destroy_check = 0
        self.some_item_id = -1

        self._showItemInfo()
        self.addMenuIcons()
        self.update_idletasks()
        self.minsize(self.winfo_reqwidth(), self.winfo_reqheight())

    def setMinHeight(self):
        height = self.winfo_height()
        width = self.winfo_width()
        self.minsize(width=width, height=height)

    def addMenuIcons(self):
        widgets = self.item_menu.winfo_children()
        for widget in widgets:
            widget.destroy()

        # reset check ...
        self.destroy_check = 0

        if self.item.get("equipped", "0") == "1":
            unequip_icon = ImageTk.PhotoImage(file="img/unequip_l.png")
            unequip_button = tk.Button(
                self.item_menu,
                image=unequip_icon,
                command=self.unequipItem
            )
            unequip_button.image = unequip_icon
            if self.item.get("type") != it.IMPLANT:
                unequip_button.pack(side=tk.LEFT)
                ToolTip(unequip_button, msg.IE_TT_UNEQUIP)
        else:
            item_type = self.item.get("type", "")
            if item_type in self.app.itemlist.EQUIPPABLE:
                show = True
                # tools are not always equippable ...
                if item_type == config.ItemTypes.TOOLS:
                    container = self.item.find("container")
                    damage = self.item.find("damage")
                    if container is None and damage is None:
                        show = False

                equip_icon = ImageTk.PhotoImage(file="img/equip_l.png")
                equip_button = tk.Button(
                    self.item_menu,
                    image=equip_icon,
                    command=self.equipItem
                )
                equip_button.image = equip_icon
                if show:
                    equip_button.pack(side=tk.LEFT)
                    ToolTip(equip_button, msg.IE_TT_EQUIP)

        if int(self.item_quantity) > 1:
            self.split_number.set("1")
            split_scroller = tk.Spinbox(
                self.item_menu,
                textvariable=self.split_number,
                width=2,
                from_=1,
                to=int(self.item_quantity) - 1
            )
            ToolTip(split_scroller, msg.IE_TT_SPLIT_AMOUNT)
            split_scroller.pack(side=tk.LEFT, fill=tk.Y)
            split_icon = ImageTk.PhotoImage(file="img/split.png")
            split_button = tk.Button(
                self.item_menu,
                image=split_icon,
                command=self.split
            )
            split_button.image = split_icon
            split_button.pack(side=tk.LEFT)
            ToolTip(split_button, msg.IE_TT_SPLIT)
        
        if self.char.getIdenticalItem(self.item) is not None:
            condense_icon = ImageTk.PhotoImage(file="img/join.png")
            condense_button = tk.Button(
                self.item_menu,
                image=condense_icon,
                command=self.condense
            )
            condense_button.image = condense_icon
            condense_button.pack(side=tk.LEFT)
            ToolTip(condense_button, msg.IE_TT_CONDENSE)

        sell_icon = ImageTk.PhotoImage(file="img/money.png")
        sell_button = tk.Button(
            self.item_menu,
            image=sell_icon,
            command=self.sellItem
        )
        sell_button.image = sell_icon
        sell_button.pack(side=tk.LEFT)
        ToolTip(sell_button, msg.IE_TT_SELL)

        destroy_icon = ImageTk.PhotoImage(file="img/cross.png")
        destroy_button = tk.Button(
            self.item_menu,
            image=destroy_icon,
            command=self.destroyItem
        )
        destroy_button.image = destroy_icon
        if self.char.getEditMode() == "generation":
            destroy_button.state(["disabled"])
        destroy_button.pack(side=tk.LEFT)
        ToolTip(destroy_button, msg.IE_TT_DESTROY)

    # This method shows the information for that item 
    def _showItemInfo(self):
        """ Display the item info in the main screen section
        """

        item_title = self.item_title
        item_body = self.item_body

        # clear the frames (if necessary)
        widgets = item_title.winfo_children()
        for widget in widgets:
            widget.destroy()

        widgets = item_body.winfo_children()
        for widget in widgets:
            widget.destroy()

        quant_label = tk.Label(
            item_title,
            text=str(self.item_quantity) + "x - ",
            font="Helvetica 12 bold")
        quant_label.pack(side=tk.LEFT)

        name_label = tk.Entry(
            item_title,
            font="Helvetica 12 bold",
            style="edit_entry"
        )
        name_label.insert(0, self.item_name)
        name_label.state(["disabled"])
        name_label.pack(side=tk.LEFT, expand=1)
        name_label.bind("<Double-Button-1>", self._activateEntryField)
        name_label.bind(
            "<Return>",
            lambda event:
                self._updateAttribute(event, attribute="name")
        )

        weight = self.getWeight()
        if weight > 500: 
            weight_str = str(round(weight/1000.0, 2))
            weight_str = weight_str.replace(".", ",") + msg.IE_KG
        else: 
            weight_str = str(weight) + msg.IE_G 

        weight_str = msg.IE_WEIGHT + weight_str
        
        weight_label = tk.Label(item_body, text=weight_str)
        weight_label.pack(fill=tk.X)

        price = round(self.item_price * self.item_quantity, 2)
        price = str(price)
        if "." in price:
            price = price.split(".")
            price[1] = price[1] + "0000"
            price[1] = price[1][0:2]
            price = msg.MONEYSPLIT.join(price)
        price_str = msg.IE_PRICE_VALUE + price
        price_label = tk.Label(item_body, text=price_str)
        price_label.pack(fill=tk.X)

        qualtities = {
            1: msg.IE_QUALITY_1,
            2: msg.IE_QUALITY_2,
            3: msg.IE_QUALITY_3,
            4: msg.IE_QUALITY_4,
            5: msg.IE_QUALITY_5,
            6: msg.IE_QUALITY_6,
            7: msg.IE_QUALITY_7,
            8: msg.IE_QUALITY_8,
            9: msg.IE_QUALITY_9,
        }
        quality_str = msg.IE_QUALITY + ": " + qualtities[self.item_quality]
        quality_frame = tk.Frame(item_body)
        quality_label = tk.Label(
            quality_frame,
            text=quality_str,
        )
        quality_label.pack(side=tk.LEFT)
        rep_icon = ImageTk.PhotoImage(file="img/repair.png")
        rep_label = tk.Label(quality_frame, image=rep_icon)
        rep_label.bind("<Button-1>", self.repair)
        rep_label.image = rep_icon
        ToolTip(rep_label, msg.IE_TT_REPAIR)
        if self.item_quality >= 9:
            rep_label.state(["disabled"])

        rep_label.pack(side=tk.RIGHT, anchor=tk.W)
        dmg_icon = ImageTk.PhotoImage(file="img/damage.png")
        dmg_label = tk.Label(quality_frame, image=dmg_icon)
        dmg_label.bind("<Button-1>", self.damage)
        dmg_label.image = dmg_icon
        dmg_label.pack(side=tk.RIGHT, anchor=tk.W)
        ToolTip(dmg_label, msg.IE_TT_DAMAGE_ITEM)
        if self.item_quality <= 1:
            dmg_label.state(["disabled"])

        quality_frame.pack(fill=tk.X)

        options = self.item.findall("option")
        for option in options:
            name = option.get("name", "")
            value = option.get("value", "")
            frame = tk.Frame(self.item_body)
            display_name = ""
            if name == it.OPTION_CALIBER:
                display_name = msg.IE_CALIBER
            elif name == it.OPTION_COLOR:
                display_name = msg.IE_CE_FABRIC_COLOR
            else:
                display_name = name
            tk.Label(
                frame,
                text=display_name
            ).pack(side=tk.LEFT, anchor=tk.W)
            entry = tk.Entry(
                frame,
                width=len(value)+2,
                style="edit_entry"
            )
            entry.delete(0, tk.END)
            entry.insert(0, value)
            entry.state(["disabled"])
            entry.bind("<Double-Button-1>", self._activateEntryField)
            entry.bind(
                "<Return>",
                lambda event, name=name:
                    self._updateTag(event, tagname="option", name=name)
            )
            entry.pack(side=tk.RIGHT, anchor=tk.E)
            frame.pack()

        # display stuff according to item type ...
        self.showMore(item_body)

        # display the description Window ...
        description_text = tk.Text(
            item_body,
            width=30,
            height=8,
            wrap=tk.WORD,
            font="Helvetica 9"
        )
        description_text.bind("<KeyRelease>", self.descriptionEdited)
        description_text.pack(fill=tk.X)
        description = self.item.find("description")
        if description is not None:
            description_text.insert(tk.END, description.text)

    def showMore(self, frame):
        # call the specialized information based on the item type ...
        item_type = self.item.get("type")
        containers = [
            it.BAG,
            it.BOX,
            it.CONTAINER,
            it.TOOLS,
            it.HARNESS
        ]
        sa_weapons = [
            it.REVOLVER,
            it.RIFLE_SA,
            it.SHOT_GUN_SA
        ]
        ha_weapons = [
            it.PISTOL,
            it.RIFLE,
            it.SHOT_GUN,
            it.AUTOMATIC_WEAPON
        ]
        melee_weapons = [
            it.CLUB,
            it.BLADE,
            it.STAFF,
            it.OTHER_MELEE,
            it.NATURAL
        ]
        biotech = [
            it.IMPLANT,
            it.IMPLANT_PART,
            it.PROSTHESIS
        ]

        if item_type in containers:
            container_tag = self.item.find("container")
            if container_tag is not None:
                self.showContent(frame)
        elif item_type in melee_weapons:
            self.getMeleeInfo(frame)
        elif item_type == it.CLIP:
            self.getClipInfo(frame)
        elif item_type in sa_weapons:
            self.getRevolverInfo(frame)
        elif item_type in ha_weapons:
            self.getPistolInfo(frame)
        elif item_type == it.AMMO:
            self.getAmmoInfo(frame)
        elif item_type in biotech:
            self.getBiotechInfo(frame, item_type)

    # try to set the active chamber of a multi chambered weapon
    def selectChamber(self, event, number):
        """Selecting the chamber
        event: an event as normally called by a button click
        number: int - the intended chamber
        """

        selected = self.char.setActiveChamber(self.item, number)
        if selected:
            widgets = self.widgets["chambers"].winfo_children()
            for widget in widgets:
                widget.state(["!pressed"])
            active = self.widgets["chamber"+str(number)]
            active.state(["pressed"])

    # load a round into the active chamber
    def loadRoundInChamber(self, event, item, mode="weapon"):
        """This method is used to load an ammo item into the active chamber

        Args:
            event(Event): triggering the load
            mode(str):  "weapon" - the item is the weapon
                        "ammo" - the item is the bullet
            item (Element<item>): the other item
        """

        if mode == "weapon":
            weapon = self.item
            ammo = item
        else:
            weapon = item
            ammo = self.item
        loaded = self.char.loadRoundInChamber(ammo, weapon)
        if loaded: 
            self.char.setActiveChamber(self.item, "next")
            self._showItemInfo()
            self.app.updateItemList()
            self.addMenuIcons()

    def reloadChamber(self, event, item, variant="weapon"):
        """ 'Working the slide'
        The first round from the clip will be loaded into the chamber
        if there is already a round loaded it will be ejected (to the inventory)

        Args:
            event(Event): the triggering event
            item (Element<item>): bullet to be loaded into the gun
            variant(str)="weapon":
        """

        if variant == "weapon":
            weapon = self.item
            bullet = item
        else:
            bullet = self.item
            weapon = item

        self.char.reloadChamber(bullet, weapon)
        self._showItemInfo()
        self.app.updateItemList()
        self.addMenuIcons()

        new_quantity = self.item.get("quantity")
        self.item_quantity = new_quantity
        
        if variant != "weapon" and new_quantity == "1":
            self.close()
        
    # loading rounds into a clip
    def loadRoundInClip(self, event, item, fill=True):
        """ Loading rounds into a clip item.
        event: this method is triggered by a tk.Event
        item: the the rounds to load
        line: tk.Frame holding 

        """
        # it must be a single clip!!
        quantity = int(self.item.get("quantity"))
        if quantity > 1:
            self.char.splitItemStack(self.item, quantity - 1)

        # add one
        if not fill: 
            self.char.loadRoundInClip(item, self.item)
        
        # or many
        while fill:
            fill = self.char.loadRoundInClip(item, self.item)
            if item.get("quantity") == "1":
                break
        
        self._showItemInfo()
        self.app.updateItemList()
        self.addMenuIcons()

    # this method loads a clip into a weapon
    def loadClip(self, event, item):
        self.char.packItem(item, self.item)
        self.app.updateItemList()
        self._showItemInfo()
        self.addMenuIcons()
        pass

    # eject the clip from a weapon
    def ejectClip(self, event, item):
        self.char.unpackItem(item)
        self.app.updateItemList()
        self._showItemInfo()
        self.addMenuIcons()

    # remove all items from the chambers (full and empty bullets)
    def ejectBullets(self):
        ammo_tag = self.item.find("ammo")
        if ammo_tag is not None:
            loaded_list = ammo_tag.get("loaded", "x").split()
            if loaded_list[0] != "x":
                for ammo_id in loaded_list:
                    ammo = self.char.getItemById(ammo_id)
                    if ammo is not None:
                        self.char.unpackItem(ammo)
            chambers = int(ammo_tag.get("chambers", "1"))
            loaded = "-1 " * chambers
            loaded = loaded.strip()
            ammo_tag.set("loaded", loaded)
            self.char.logEvent(self.item)  # for integrity reasons
        self._showItemInfo()
        self.app.updateItemList()

    # fire a weapon, spend the bullet, retrieve a empty casing ... 
    def fireWeapon(self):
        active_chamber = self.char.getActiveChamber(self.item)
        loaded_round = self.char.getRoundFromChamber(self.item, active_chamber)
        if loaded_round is not None:
            # spend round ... 
            loaded_round.set("name", msg.IE_SHELL_CASING)
            weight = int(int(loaded_round.get("weight", "0")) / 10)
            loaded_round.set("weight", str(weight))
            value = float(float(loaded_round.get("price", "0")) / 10)
            loaded_round.find("damage").set("value", "0/0")
        sa_weapons = [it.REVOLVER, it.RIFLE_SA, it.SHOT_GUN_SA]
        if self.item.get("type") in sa_weapons:
            self.char.setActiveChamber(self.item, "next")
            self._showItemInfo()
        ha_weapons = [
            it.PISTOL,
            it.RIFLE,
            it.SHOT_GUN,
            it.AUTOMATIC_WEAPON
        ]
        if self.item.get("type") in ha_weapons:
            content_list = self.item.get("content", "x").split()
            
            # get the next round 
            clip = None
            next_round = None
            for item_id in content_list:
                content_item = self.char.getItemById(item_id)
                if content_item is not None:
                    content_item_type = content_item.get("type", "")
                    if content_item_type == it.CLIP:
                        clip = content_item
                        break
            if clip is not None:
                clip_content = clip.get("content", "x").split()
                next_round = self.char.getItemById(clip_content[0])
            self.char.reloadChamber(next_round, self.item)

            self._showItemInfo()
            self.addMenuIcons()
            self.app.updateItemList()

    # condense all identical items 
    def condense(self):
        
        self.item_quantity = self.char.condenseItem(self.item)

        # now update the title string and the rebuild the item list ...
        self._showItemInfo()
        self.app.updateItemList()
        self.addMenuIcons()

    # execute the split based on the selected value
    def split(self):
        # get the split_amount
        split_amount = 0
        try:
            split_amount = int(self.split_number.get())
        except ValueError:
            pass

        if split_amount > 0 and self.item_quantity > 1:
            quantity, new_item_id = self.char.splitItemStack(
                self.item,
                split_amount
            )

            self.item_quantity = quantity

            # update the entry
            self._showItemInfo()
            self.app.updateItemList()
            self.addMenuIcons()

    # this method is invoked if the player sells an item ...
    def sellItem(self):
        price = float(self.item.get("price", "0"))
        quantity = int(self.item.get("quantity", "1"))
        self.char.unpackItem(self.item)

        sub_item_ids = self.item.get("content", "").split()
        for sub_item_id in sub_item_ids:
            sub_item = self.char.getItemById(sub_item_id)
            if sub_item is not None:
                self.char.unpackItem(sub_item)
        self.char.logEvent(self.item, op=msg.CHAR_ITEM_SELL)
        self.char.setItemQuantity(self.item, 0)
        self.char.updateAccount(price * quantity)
        self.app.updateItemList()
        self.close()

    # unequip an item: called by unequip_button 
    def unequipItem(self):
        self.char.unequipItem(self.item)
        self.app.updateItemList()
        self._showItemInfo()
        self.addMenuIcons()

    # equip an item: called by equip_button
    def equipItem(self):
        self.char.unpackItem(self.item, equip=True)
        self.app.updateItemList()
        self._showItemInfo()
        self.addMenuIcons()

        # self.close(load=self.item)

    def destroyItem(self):
        destroy = tkmb.askyesno(
            msg.IE_DEL_TITLE,
            msg.IE_DEL_TEXT,
            parent=self,
            icon=tkmb.WARNING
        )

        if destroy:
            sub_item_ids = self.item.get("content", "")
            sub_item_ids = sub_item_ids.split()
            for sub_item_id in sub_item_ids:
                sub_item = self.char.getItemById(sub_item_id)
                if sub_item is not None:
                    self.char.unpackItem(sub_item)

            self.char.logEvent(self.item, op=msg.CHAR_ITEM_DESTROY)
            self.char.setItemQuantity(self.item, 0)
            self.app.updateItemList()
            self.close(destroy=True)

    # unpack an Item 
    def unpackItem(self, event, sub_item, line_widget):
        self.char.unpackItem(sub_item)
        line_widget.destroy()
        self.app.updateItemList()

    def unpackProsthesis(self, sub_item):
        self.char.unpackItem(sub_item),

        self.close(load=self.item)

    def packItem(self, sub_item):
        self.char.packItem(sub_item, self.item)
        self.app.updateItemList()
        self.close(load=self.item)

    # retrieve weight of an item with all sub_items recursivly  ... 
    def getWeight(self):
        weight = self.char.getWeight(self.item)
        return weight

    # store the edited description as a string
    # within the close() method the data will be written to the item ...
    def descriptionEdited(self, event):
        self.description_content = event.widget.get("1.0", tk.END)

    def itemId(self):
        return self.item.get("id")

    # display content of a container item
    def showContent(self, frame):
        content_ids = self.item.get("content", "")
        content_ids = content_ids.split(" ")
        content_frame = tk.LabelFrame(frame, text=msg.IE_CONTENT)
        for content_id in content_ids:
            sub_item = self.char.getItemById(content_id)
            if sub_item is not None:
                sub_item_id = sub_item.get("id")
                line = tk.Frame(content_frame)
                label_text = sub_item.get("quantity") + "x - " + sub_item.get("name")
                label = tk.Label(line, text=label_text)
                label.bind(
                    "<Button-1>",
                    lambda event, load_item=sub_item:
                        self.close(load=load_item)
                )
                label.pack(side=tk.LEFT)
                unpack_icon = ImageTk.PhotoImage(file="img/unpack.png")
                unpack_button = tk.Button(line, image=unpack_icon)
                unpack_button.image = unpack_icon
                ToolTip(unpack_button, msg.IE_TT_UNPACK)
                unpack_button.bind(
                    "<Button-1>",
                    lambda event, sub=sub_item, line_widget=line:
                        self.unpackItem(event, sub, line_widget)
                )
                unpack_button.pack(side=tk.RIGHT, anchor=tk.E)
                line.pack(fill=tk.X, expand=1)
        content_frame.pack(fill=tk.X, expand=1)

    def getMeleeInfo(self, frame):
        damage_tag = self.item.find("damage")
        if damage_tag is not None:
            damage = damage_tag.get("value")
            text = msg.IE_DAMAGE.format(value=damage)
            tk.Label(frame,text=text).pack(fill=tk.X)

    # this method gets the revolver screen ... 
    def getRevolverInfo(self, frame):
        number_chambers = int(self.item.find("ammo").get("chambers"))
        active_chamber = int(self.item.find("ammo").get("active", "1"))
        loaded_ammo = self.item.find("ammo").get("loaded", "-1")
        ammo_list = loaded_ammo.split()
        while len(ammo_list) < number_chambers:
            ammo_list.append("-1")
            
        chamber_frame = tk.LabelFrame(frame, text=msg.IE_CHAMBERS)
            
        i = 0
        self.widgets["chambers"] = chamber_frame
        while i < number_chambers:
            loaded_item = None
            if len(ammo_list) > i:
                loaded_item = self.char.getItemById(str(ammo_list[i]))
            text = msg.IE_EMPTY
            if loaded_item is not None:
                text = loaded_item.get("name")
                
            chamber_button = tk.Button(chamber_frame, text=text)
            self.widgets["chamber"+str(i+1)] = chamber_button
            chamber_button.bind(
                "<Button-1>",
                lambda event, chamber=i+1:
                    self.selectChamber(event, chamber)
            )
            chamber_button.pack(fill=tk.X, expand=1)
            if i == active_chamber - 1:
                chamber_button.state(["pressed"])
            i += 1
        chamber_frame.pack(fill=tk.X, expand=1)

        chambered_item = self.char.getItemById(ammo_list[active_chamber-1])
        if chambered_item is not None:
            if chambered_item.get("name") == msg.IE_SHELL_CASING:
                chambered_item = None

        fire_button = tk.Button(
            chamber_frame,
            text=msg.IE_FIRE_WEAPON,
            command=self.fireWeapon
        )

        if chambered_item is None or self.char.getEditMode() == "generation":
            fire_button.config(state=tk.DISABLED)
        fire_button.pack(fill=tk.X)

        eject_button = tk.Button(
            chamber_frame, text=msg.IE_CLEAR,
            command=self.ejectBullets
        )
        eject_button.pack(fill=tk.X)

        select_label = tk.Label(frame, text=msg.IE_AVAILABLE_AMMO)
        search = "option[@name='"+it.OPTION_CALIBER+"']"
        caliber = self.item.find(search).get("value")
        items = self.getMatchingAmmo(caliber)
        if items:
            select_label.pack()
        for item in items: 
            line = tk.Frame(frame)
            item_id = item.get("id")
            ammo_button = tk.Button(line, text=item.get("name"))
            ammo_button.bind(
                "<Button-1>",
                lambda event, item=item, line=line:
                self.loadRoundInChamber(event, item))
            ammo_button.pack(side=tk.RIGHT)
            line.pack()

    # this creates the infoscreen for a half and full automatic weapon ... 
    def getPistolInfo(self, frame):
        chambered_id = self.item.find("ammo").get("loaded", "-1")
        chambered_item = self.char.getItemById(str(chambered_id))
        first_round = None
        chamber_frame = tk.LabelFrame(frame, text=msg.IE_LOADED)
        chamber_frame.pack(fill=tk.X, expand=1)
        if chambered_item is not None:
            chamber_info = tk.Label(
                chamber_frame,
                text=chambered_item.get("name")
            )
            chamber_info.pack(fill=tk.X, expand=1)
        else:
            chamber_frame.config(text=msg.IE_NOT_LOADED)
        
        loaded_clip = None
        content = self.item.get("content", "-1").split()
        for item_id in content:
            item = self.char.getItemById(item_id)
            if item is not None: 
                if item.get("type") == it.CLIP:
                    loaded_clip = item
                    break
        if loaded_clip is None:
            label = tk.Label(
                frame,
                text=msg.IE_NO_CLIP_LOADED,
                borderwidth=2,
                relief=tk.RIDGE
            )
            label.pack(fill=tk.X)
        else:
            loaded_clip_frame = tk.LabelFrame(
                frame, text=msg.IE_CLIP_LOADED
            )
            loaded_rounds = 0
            loaded_clip_content = loaded_clip.get("content", "-1").split()
            try:
                first_round = self.char.getItemById(loaded_clip_content[0])
            except IndexError:
                pass
            if first_round is not None:
                loaded_rounds = len(loaded_clip_content)
            capacity = loaded_clip.find("container").get("size")
            info = msg.IE_CLIP_STATUS + str(loaded_rounds)+" / "+str(capacity)
            content_label = tk.Label(loaded_clip_frame, text=info)
            content_label.pack(fill=tk.X, expand=1)
            eject_button = tk.Button(loaded_clip_frame, text=msg.IE_EJECT)
            eject_button.bind(
                "<Button-1>",
                lambda event, clip=loaded_clip:
                self.ejectClip(event, clip)
            )
            eject_button.pack(fill=tk.X, expand=1)
            loaded_clip_frame.pack(fill=tk.X, expand=1)

        fire_button = tk.Button(
            chamber_frame,
            text=msg.IE_FIRE_WEAPON,
            command=self.fireWeapon
        )
        if chambered_item is None or self.char.getEditMode() == "generation":
            fire_button.config(state=tk.DISABLED)
        fire_button.pack(fill=tk.X)

        reload_button = tk.Button(chamber_frame, text=msg.IE_CYCLE_WEAPON)
        reload_button.bind(
            "<Button-1>",
            lambda event, item=first_round:
            self.reloadChamber(event, item))
        reload_button.pack(fill=tk.X)

        search = "option[@name='"+it.OPTION_CALIBER+"']"
        caliber = self.item.find(search).get("value")
        clips = self.getMatchingAmmo(caliber, it.CLIP)
        if clips: 
            clips_label = tk.Label(frame, text=msg.IE_COMPATIBLE_CLIPS)
            clips_label.pack()

        for clip in clips: 
            clip_frame = tk.Frame(frame, borderwidth="1", relief=tk.RIDGE)

            name_frame = tk.Label(clip_frame)
            name_frame.pack(fill=tk.X, expand=1)
            clip_capacity = clip.find("container").get("size")
            clip_contents = "0"
            content = clip.get("content", "-1").split()
            try:
                first_round = self.char.getItemById(content[0])
            except IndexError:
                first_round = None
            if first_round is not None:
                clip_contents = str(len(content))
                info = first_round.get("name") + " [" + first_round.find("damage").get("value") + "]"
                first_round_label = tk.Label(clip_frame, text=info)
                first_round_label.pack(fill=tk.X, expand=1)
            if loaded_clip is None:
                load_button = tk.Button(clip_frame, text=msg.IE_LOAD_WEAPON)
                load_button.bind(
                    "<Button-1>",
                    lambda event, item=clip:
                        self.loadClip(event, item)
                )
                load_button.pack(fill=tk.X, expand=1)
            name = clip.get("name") + " ("+clip_contents+"/"+clip_capacity+")"
            name_frame.config(text=name)

            clip_frame.pack(fill=tk.X, expand=1)
    
    # display information for clips ... 
    def getClipInfo(self, frame):
        self.showContent(frame)
        search = "option[@name='" + it.OPTION_CALIBER + "']"
        caliber = self.item.find(search).get("value")
        size = self.item.find("container").get("size")
        items = self.getMatchingAmmo(caliber)
        for item in items:
            line = tk.Frame(frame)
            item_id = item.get("id")
            name_label = tk.Label(line, text=item.get("name"))
            name_label.pack(side=tk.LEFT)
            button_fill = tk.Button(line, text=msg.IE_FILL_CLIP)
            button_fill.bind(
                "<Button-1>",
                lambda event, item=item:
                    self.loadRoundInClip(event, item, fill=True)
            )
            button_fill.pack(side=tk.RIGHT)
            button_plus1 = tk.Button(line, text=msg.IE_ADD_ONE)
            button_plus1.bind(
                "<Button-1>",
                lambda event, item=item:
                    self.loadRoundInClip(event, item, fill=False)
            )
            button_plus1.pack(side=tk.RIGHT)
            line.pack() 

    # display information for ammo .... 
    def getAmmoInfo(self, frame):
        search = "option[@name='"+it.OPTION_CALIBER+"']"
        caliber = self.item.find(search).get("value")
        
        items = self.char.getItems()
        guns = []
        for item in items: 
            # try to get the caliber of the item ...
            item_caliber = item.find("option[@name='"+it.OPTION_CALIBER+"']")
            if item_caliber is not None: 
                # make sure it is a weapon ...
                if (item_caliber.get("value") == caliber
                    and item.get("type") not in [it.AMMO, it.CLIP]
                ):
                    # add the item to the list of guns ...
                    guns.append(item)
        if guns:
            info = tk.Label(frame, text=msg.IE_INSERT_CARTRIDGE)
            info.pack()
        for gun in guns:
            button = tk.Button(frame, text=gun.get("name"))
            button.pack(fill=tk.X, expand=1)
            button.bind(
                "<Button-1>",
                lambda event, item=gun:
                    self.reloadChamber(event, item, variant="bullet")
            )

    # display information for implants
    def getBiotechInfo(self, frame, item_type):

        implanted = int(self.item.get("equipped", "0"))

        inside = self.item.get("inside", "-1")
        if inside != -1:
            parent = self.char.getItemById(inside)
            if parent is not None:
                name = parent.get("name")
                parent_type = parent.get("type")
                if parent_type in [it.IMPLANT, it.PROSTHESIS]:
                    if item_type == it.PROSTHESIS:
                        status = msg.IE_ATTACHED_TO
                    else:
                        status = msg.IE_BUILT_INTO
                    label = tk.Label(
                        frame,
                        text=status+name
                    )
                    label.bind(
                        "<Button-1>",
                        lambda item=parent:
                            self.close(load=parent)
                    )
                    label.pack()

        content = self.item.get("content", "")
        if content != "":
            content_list = content.split()
        else:
            content_list = []
        content_frame = tk.LabelFrame(frame, text=msg.IE_IMPLANT_ADDONS)
        for item_id in content_list:
            sub_item = self.char.getItemById(item_id)
            if sub_item is not None:
                item_frame = tk.Frame(content_frame)
                sub_name = sub_item.get("name")
                sub_type = sub_item.get("type")
                label = tk.Label(
                    item_frame,
                    text=sub_name
                )
                label.bind(
                    "<Button-1>",
                    lambda event, sub_item=sub_item:
                        self.close(load=sub_item)
                )
                label.pack(side=tk.LEFT, anchor=tk.W)
                button = tk.Button(
                    item_frame,
                    text=msg.IE_UNEQUIP,
                    command=lambda sub_item=sub_item:
                        self.unpackProsthesis(sub_item)
                )
                if sub_type == it.PROSTHESIS:
                    button.pack(side=tk.RIGHT, anchor=tk.E)
                item_frame.pack(fill=tk.X)

        if content_list:
            content_frame.pack(fill=tk.X)

        if item_type != it.IMPLANT_PART:
            add_ons = (self.char.getItems(item_type=it.IMPLANT_PART)
                    + self.char.getItems(item_type=it.PROSTHESIS))
            for sub_item in add_ons:
                inside = sub_item.get("inside", "-1")
                sub_id = sub_item.get("id")
                if (inside != "-1"
                    or self.item.get("id") in sub_item.get("content", "").split()
                    or sub_id == self.item.get("id")
                ):
                    continue
                sub_name = sub_item.get("name")
                if sub_id not in content_list:
                    sub_frame = tk.Frame(frame)
                    label = tk.Label(
                        sub_frame,
                        text=sub_name
                    )
                    label.pack(side=tk.LEFT, anchor=tk.W)
                    button = tk.Button(
                        sub_frame,
                        text="einbauen",
                        command=lambda sub_item=sub_item:
                            self.packItem(sub_item)
                    )
                    button.pack(side=tk.RIGHT, anchor=tk.E)
                    sub_frame.pack(fill=tk.X)

        if item_type == it.IMPLANT and not implanted:
            tk.Button(
                frame,
                text=msg.IE_IMPLANT,
                command=self.equipItem
            ).pack(fill=tk.X)

        items = self.char.getItems(item_type=it.IMPLANT_PART)
        for item in items:
            pass

    # find matching ammo in inventory ...
    def getMatchingAmmo(self, caliber, search_type=it.AMMO):
        items = self.char.getItems()
        ammo = []
        for item in items: 
            item_type = item.get("type")
            if item_type == search_type:
                search = "option[@name='"+it.OPTION_CALIBER+"']"
                if item.find(search).get("value") == caliber:
                    inside = item.get("inside", "-1")
                    available = False
                    if inside == "-1":
                        available = True
                    elif inside != "-1":
                        container_type = self.char.getItemById(inside).get("type")
                        if container_type in [it.BAG, it.HARNESS]:
                            available = True

                    if available:
                        ammo.append(item)
        return ammo

    def damage(self, event):
        if "disabled" in event.widget.state():
            return
        self.item_quality -= 1
        self.item_price *= .666
        self.item.set("quality", str(self.item_quality))
        self.item.set("price", str(self.item_price))
        self.char.logEvent(
            self.item,
            op=msg.CHAR_ITEM_DAMAGED,
            mod=str(self.item_quality)
        )

        self._showItemInfo()
        pass

    def repair(self, event):
        if "disabled" in event.widget.state():
            return
        self.item_quality += 1
        self.item_price *= 1.25
        self.item.set("quality", str(self.item_quality))
        self.item.set("price", str(self.item_price))
        self.char.logEvent(
            self.item,
            op=msg.CHAR_ITEM_REPAIRED,
            mod=str(self.item_quality)
        )

        self._showItemInfo()
        pass


    # this is called to close the window (or switch the item ...)
    def close(self, load=None, destroy=False):
        if not destroy and len(self.description_content) > 1: 
            self.item.find("description").text = self.description_content
            self.char.logEvent(self.item, op=msg.CHAR_ITEM_DESCRIPTION)
                
        # destroy window and remove from list
        self.destroy()
        self.app.open_windows["itemedit"] = 0

        # create new window if a subitem is called
        if load is not None:
            self.app.open_windows["itemedit"] = ItemEditor(self.app, load)
            self.app.updateItemList()

    # activate the entry field ...
    @staticmethod
    def _activateEntryField(event):
        entry = event.widget
        entry.config(state=tk.NORMAL)

    # updating an item attribute
    def _updateAttribute(self, event, attribute):
        """ This method is used to update a specific item attribute
        event: tk.Event()
        attribute: string - attribute to update valid
            (name,quantity,quality,weight,price)
        """

        entry = event.widget
        new_value = entry.get()

        old_value = self.item.get(attribute)

        regex_string = "[^a-zA-Z0-9 .,:\(\)\[\]\!\xE4\xF6\xFC\xC4\xD6\xDC\xDF]" 
        if re.findall(regex_string, new_value):
            entry.config(foreground="#ff0000")
        else:
            entry.config(foreground="#000000", state=tk.DISABLED)
            if new_value != old_value:
                if attribute == "name":
                    mod_info = self.item.get(attribute)
                    op = msg.CHAR_ITEM_RENAMED
                else:
                    mod_info = attribute+":"+new_value
                    op = msg.CHAR_UPDATE
                    
                self.item.set(attribute, new_value)
                self.char.logEvent(
                    self.item,
                    mod=mod_info,
                    op=msg.CHAR_UPDATE
                )
                self.app.updateItemList()

    # updating an item tag
    def _updateTag(self, event, tagname, name=None):
        """ This method is used to update an item tag
        event: tk.event
        tagname: string - xml name of tag
        (valid tags: option, damage, container)
        name: string - name of option (not used in the tags ...)
        """

        entry = event.widget
        new_value = entry.get()
        if name is not None: 
            tag = self.item.find(tagname+"[@name='"+name+"']")
        else: 
            tag = self.item.find(tagname)

        old_value = tag.get("value", "")

        regex_string = "[^a-zA-Z0-9 .,:\(\)\[\]\!\xE4\xF6\xFC\xC4\xD6\xDC\xDF]" 
        if re.findall(regex_string, new_value):
            entry.config(foreground="#ff0000")
        else:
            entry.config(
                foreground="#000000",
                width=len(new_value) + 2,
                state=tk.DISABLED
            )
            if new_value != old_value:
                tag.set("value", new_value)
                mod_info = tagname+":"+new_value
                self.char.logEvent(
                    self.item,
                    mod=mod_info,
                    op=msg.CHAR_UPDATE
                )
