# coding=utf-8
import tkinter as tk
import xml.etree.ElementTree as et
from itemeditor import ItemEditor
from inventoryeditor import InventoryEditor
import config

it = config.ItemTypes()
msg = config.Messages()


class EquipmentScreen(tk.Frame):
    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.char = app.char
        self.itemlist = app.itemlist

        self.account_info = tk.StringVar()

        self.active_bag_id = -1
        self.open_windows = app.open_windows

        # define the three columns
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(
            side=tk.LEFT,
            anchor=tk.N,
            fill=tk.Y
        )

        # displaying the characters initial account
        self.initial_account_frame = tk.Frame(self.left_frame)
        mode = self.char.getEditMode()
        if mode == "generation":
            self.reduce_account = tk.Button(
                self.initial_account_frame,
                text=" - ",
                command=lambda: self.initialAccount(-1)
            )
            self.reduce_account.pack(side=tk.LEFT, anchor=tk.W)
        account_label = tk.Label(
            self.initial_account_frame,
            textvariable=self.account_info
        )
        account_label.pack(side=tk.LEFT, fill=tk.X, expand=1)
        if mode == "generation":
            self.increase_account = tk.Button(
                self.initial_account_frame,
                text=" + ",
                command=lambda: self.initialAccount(+1)
            )
            self.increase_account.pack(side=tk.LEFT, anchor=tk.E)
        self.initial_account_frame.pack(fill=tk.X, expand=1)
        self.initialAccount()

        # a button to buy new stuff (opens the InventoryEditor)
        self.buy_button = tk.Button(
            self.left_frame,
            text=msg.ES_BUY_BUTTON,
            command=self.displayInventoryEditor
        )
        self.buy_button.pack(fill=tk.X)

        # show equipped items 
        self.equipped_frame = tk.LabelFrame(
            self.left_frame,
            text=msg.ES_EQUIPPED,
            font="Arial 10 bold"
        )
        self.equipped_canvas = tk.Canvas(
            self.equipped_frame,
            width=250,
            height=450
        )
        self.equipped_canvas.pack(side=tk.LEFT)
        self.equipped_scroll = tk.Scrollbar(
            self.equipped_frame,
            orient=tk.VERTICAL
        )
        self.equipped_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.equipped_scroll.config(
            command=self.equipped_canvas.yview
        )
        self.equipped_canvas.config(
            yscrollcommand=self.equipped_scroll.set
        )
        self.equipped_frame.pack(fill=tk.Y)
        self.showEquippedItems()

        # center frame
        # used for the weapons
        self.center_frame = tk.Frame(self)
        self.melee_frame = tk.LabelFrame(
            self.center_frame,
            text=msg.ES_MELEE,
            font="Arial 10 bold"
        )
        self.melee_canvas = tk.Canvas(
            self.melee_frame,
            width=230,
            height=250
        )
        self.melee_canvas.pack(side=tk.LEFT)
        self.melee_scroll = tk.Scrollbar(
            self.melee_frame,
            orient=tk.VERTICAL
        )
        self.melee_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.melee_scroll.config(
            command=self.melee_canvas.yview
        )
        self.melee_canvas.config(
            yscrollcommand=self.melee_scroll.set
        )
        self.melee_frame.pack()

        self.guns_frame = tk.LabelFrame(
            self.center_frame,
            text=msg.ES_GUNS,
            font="Arial 10 bold"
        )
        self.guns_canvas = tk.Canvas(
            self.guns_frame,
            width=230,
            height=250
        )
        self.guns_canvas.pack(side=tk.LEFT)
        self.guns_scroll = tk.Scrollbar(
            self.guns_frame,
            orient=tk.VERTICAL
        )
        self.guns_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.guns_scroll.config(
            command=self.guns_canvas.yview
        )
        self.guns_canvas.config(
            yscrollcommand=self.guns_scroll.set
        )

        self.guns_frame.pack()
        self.center_frame.pack(side=tk.LEFT, anchor=tk.N)
        self.showEquippedGuns(self.guns_canvas)
        self.showEquippedMelee(self.melee_canvas)
        
        # the right frame is used for unassigned items
        self.right_frame = tk.Frame(self)
        self.unassigned_frame = tk.LabelFrame(
            self.right_frame,
            text=msg.ES_UNASSIGNED,
            font="Arial 10 bold"
        )
        self.unassigned_canvas = tk.Canvas(
            self.unassigned_frame,
            height=500,
            width=230
        )
        self.unassigned_canvas.pack(side=tk.LEFT)
        self.unassigned_scroll = tk.Scrollbar(
            self.unassigned_frame,
            orient=tk.VERTICAL
        )
        self.unassigned_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.unassigned_scroll.config(
            command=self.unassigned_canvas.yview
        )
        self.unassigned_canvas.config(
            yscrollcommand=self.unassigned_scroll.set
        )
        self.unassigned_frame.pack(fill=tk.BOTH, expand=1)
        self.right_frame.pack(side=tk.LEFT, anchor=tk.N, fill=tk.BOTH)
        self.showUnassignedItems()

    # handling the initial account ... 
    def initialAccount(self, change=0):
        """ This method is called to update the initial account

        change: int - (1 = 1000 Rand and costs 1 XP)

        the method is called on the initial creation of the
        equipment screen with value 0 - this is to initialize
        the StringVar with a value. This call does not reflect
        in the character ElementTree.
        """

        # retrieve the main account and the current value
        account = self.char.getAccount()
        initial = int(account.get("initial", "0"))

        new_value = initial + change

        # update the account and xp ..
        if change != 0:
            self.char.updateAvailableXP(-change)
            self.char.updateAccount(change*1000, reason=msg.CHAR_STARTING_CAPITAL)
        account.set("initial", str(new_value))

        # display the value ...
        initial_amount = 1000 * new_value
        text = msg.ES_INITIAL_FUNDS.format(amount=str(initial_amount))
        self.account_info.set(text)

        # disable reduce button if necessary
        if self.char.getEditMode() == "generation":
            if new_value < 1:
                self.reduce_account.config(state=tk.DISABLED)
            else:
                self.reduce_account.config(state=tk.NORMAL)

    # open the inventory editor and add it to the list of the open windows
    def displayInventoryEditor(self):
        if self.open_windows["inv"] != 0:
            self.open_windows["inv"].focus()
        else:
            self.open_windows["inv"] = InventoryEditor(self)
            self.open_windows["inv"].focus()

    # called when something has changed and the item lists need updating ...
    def updateItemList(self):
        self.showEquippedItems()
        self.showEquippedGuns(self.guns_canvas)
        self.showEquippedMelee(self.melee_canvas)
        self.showUnassignedItems()
        
    # this shows all unassigned items ...
    def showUnassignedItems(self):
        # clear the list ...
        canvas = self.unassigned_canvas
        canvas.delete(tk.ALL)

        # get all items 
        items = self.char.getItems()
        
        equippable_types = self.itemlist.EQUIPPABLE            
        y = 0
        for item in items:
            # is the item currently packed or assigned as carried item?
            unassigned = True
            inside = int(item.get("inside", "-1"))
            if inside > 0:
                unassigned = False
            equipped = int(item.get("equipped", "0"))
            if equipped == 1:
                unassigned = False

            # display unassigned items
            if unassigned: 
                quantity = int(item.get("quantity"))
                item_id = item.get("id")
                item_frame = tk.Frame(canvas)
                item_frame.columnconfigure(1, weight=100)
                amount_label = tk.Label(
                    item_frame,
                    text=str(quantity)+msg.MULTIPLY,
                    justify=tk.LEFT,
                    width=4
                )
                amount_label.grid(row=0, column=0, sticky=tk.E)
                name_label = tk.Label(
                    item_frame,
                    text=item.get("name"),
                    justify=tk.LEFT
                )
                name_label.bind(
                    "<Button-1>",
                    lambda event, item_id=item_id:
                        self.displayItemEditor(event, item_id)
                )
                name_label.grid(row=0, column=1, sticky=tk.W)
                    
                if item.get("type") in equippable_types: 
                    equip_button = tk.Button(item_frame, text="E")
                    equip_button.bind(
                        "<Button-1>",
                        lambda event, item_id=item_id:
                            self.equipItem(event, item_id)
                    )
                    equip_button.grid(row=0, column=2)
                else:
                    empty = tk.Label(item_frame, text=" ", width=2)
                    empty.grid(row=0, column=2)
                    
                if self.active_bag_id >= 0: 
                    pack_button = tk.Button(item_frame, text="P")
                    pack_button.bind(
                        "<Button-1>",
                        lambda event, item_id=item_id:
                            self.packItem(event, item_id))
                    pack_button.grid(row=0, column=3)
                else:
                    empty = tk.Label(item_frame, text=" ", width=2)
                    empty.grid(row=0, column=3)
                
                canvas.create_window(
                    0, y,  # x, y
                    window=item_frame,
                    anchor=tk.NW,
                    width=230
                )

                y += name_label.winfo_reqheight() + 5
  
    # show the equipped items
    def showEquippedItems(self):
        canvas = self.equipped_canvas
        # clear contents
        
        canvas.delete(tk.ALL)

        y = 0

        # display weight ...
        weight = tk.Label(canvas, text=self.updateWeight())
        canvas.create_window(0, y, anchor=tk.NW, window=weight)
        
        y += 25

        # armor and clothing
        armor_frame = tk.LabelFrame(
            canvas,
            text=msg.ES_CLOTHING_ARMOR,
            width=250
        )
        lines = self.showEquippedClothing(armor_frame)
        if lines > 1:
            armor = canvas.create_window(
                0, y,  # x, y
                window=armor_frame,
                anchor=tk.NW,
                width=250
            )
            self.update_idletasks()
            y += armor_frame.winfo_height()

        cyber_frame = tk.LabelFrame(
            canvas,
            text=msg.ES_BIOTECH,
            width=250
        )
        lines = self.showEquippedBiotech(cyber_frame)
        if lines > 1:
            armor = canvas.create_window(
                0, y,  # x, y
                window=cyber_frame,
                anchor=tk.NW,
                width=250
            )
            self.update_idletasks()
            y += cyber_frame.winfo_height()

        # carried bags
        bags = self.char.getContainers()
        for bag in bags:
            bag_frame = tk.Frame(canvas)
            self.showBagContents(bag, bag_frame)
            canvas.create_window(
                0, y,  # x, y
                window=bag_frame,
                anchor=tk.NW,
                width=250
            )
            self.update_idletasks()
            y += bag_frame.winfo_height()

    # show the contents of an equipped bag
    def showBagContents(self, bag, frame):
        bag_id = int(bag.get("id"))
            
        # if no bag is the active bag - this bag becomes the active bag ...
        if self.active_bag_id == -1:
            self.active_bag_id = bag_id

        bag_tag = bag.find("container")
        bag_frame = tk.LabelFrame(frame, text=bag_tag.get("name"))
            
        if self.active_bag_id == bag_id:
            bag_frame.config(foreground="#0000ff")

        # retrieve bag content and display ...
        item_ids = bag.get("content")
        
        if item_ids is not None: 
            entries = item_ids.split()
            for item_id in entries:
                item = self.char.getItemById(item_id)
                if item is not None: 
                    item_line = tk.Frame(bag_frame)
                    quantity_label = tk.Label(
                        item_line,
                        text=item.get("quantity")
                             + msg.MULTIPLY)
                    quantity_label.pack(side=tk.LEFT)
                    item_label = tk.Label(
                        item_line,
                        text=item.get("name")
                    )
                    item_label.bind(
                        "<Button-1>",
                        lambda event, id=item_id:
                            self.displayItemEditor(event, id))
                    item_label.pack(side=tk.LEFT, fill=tk.X, expand=1)
                    item_unpack = tk.Button(item_line, text="U")
                    item_unpack.bind(
                        "<Button-1>",
                        lambda event, id=item_id:
                            self.unpackItem(event, id)
                    )
                    item_unpack.pack(side=tk.RIGHT, anchor=tk.E)
                    item_line.pack(fill=tk.X, expand=1)
        
        # unequip bag ...                    
        bag_unequip = tk.Button(bag_frame, text=msg.ES_UNEQUIP)
        bag_unequip.bind(
            "<Button-1>",
            lambda event, id=str(bag_id):
                self.unequipItem(event, id)
        )
        bag_unequip.pack(fill=tk.X)
        
        bag_frame.pack(fill=tk.BOTH, expand=1)
        bag_frame.bind(
            "<Button-1>",
            lambda event, bag_id=bag_id:
                self.setActiveBag(event, bag_id)
        )

    # show equipped clothing and armor
    def showEquippedClothing(self, frame):
        items = self.char.getItems()
        row = 0
        name_label = tk.Label(frame, text=msg.ES_ITEMNAME)
        name_label.grid(row=row, column=0, columnspan=3, sticky=tk.W)
        sd_label = tk.Label(frame, text=msg.ES_DAMAGE_S)
        sd_label.grid(row=row, column=3, sticky=tk.EW)
        qual_label = tk.Label(frame, text=msg.ES_QUALITY_S)
        qual_label.grid(row=row, column=4, sticky=tk.EW)
        row = 1
        for item in items:
            
            if (item.get("equipped", "0") == "1" and
                (item.get("type") == it.CLOTHING or
                item.get("type") == it.ARMOR or
                item.get("type") == it.HARNESS)
            ):
                name = item.get("name")
                name_label = tk.Label(frame, text=name)
                name_label.grid(row=row, column=0, columnspan=3, sticky=tk.W)
                sd = ""
                damage = item.find("damage")
                if damage is not None:
                    sd = damage.get("value", "")
                sd_label = tk.Label(frame, text=sd)
                sd_label.grid(row=row, column=3, sticky=tk.EW)
                quality = item.get("quality")
                qual_label = tk.Label(frame, text=quality)
                qual_label.grid(row=row, column=4, sticky=tk.EW)
                unequip_button = tk.Button(frame, text=msg.ES_UNEQUIP_S)
                item_id = item.get("id")
                unequip_button.bind(
                    "<Button-1>", lambda event, item_id=item_id:
                        self.unequipItem(event, item_id)
                )
                unequip_button.grid(row=row, column=5, sticky=tk.EW)
                row += 1
        return row

    def showEquippedBiotech(self, frame):
        frame.columnconfigure(0, weight=100)
        items = self.char.getItems(item_type=it.IMPLANT)
        row = 0
        name_label = tk.Label(frame, text=msg.ES_ITEMNAME)
        name_label.grid(row=row, column=0, sticky=tk.W)
        qual_label = tk.Label(frame, text=msg.ES_QUALITY_S)
        qual_label.grid(row=row, column=1, sticky=tk.EW)
        row = 1
        for item in items:
            if item.get("equipped", "0") == "1":
                item_id = item.get("id")
                name = item.get("name")
                name_label = tk.Label(frame, text=name)
                name_label.grid(row=row, column=0, sticky=tk.W)
                name_label.bind(
                    "<Button-1>",
                    lambda event, item_id=item_id:
                        self.displayItemEditor(event, item_id)
                )
                quality = item.get("quality")
                qual_label = tk.Label(frame, text=quality)
                qual_label.grid(row=row, column=1, sticky=tk.EW)
                row += 1
        return row

    # display equipped melee weapons
    def showEquippedMelee(self,canvas):
        """ show the equipped melee weapons 
        canvas: tk.Canvas - where to display the stuff ...
        """
        # clear the frame 
        canvas.delete(tk.ALL)

        # get the items
        items = self.char.getItems()
        
        y = 0
        for item in items:
            if item.get("equipped", "0") == "1":
                item_type = item.get("type")
                weapons = [
                    it.CLUBS,
                    it.BLADES,
                    it.STAFFS,
                    it.OTHER_MELEE,
                    it.TOOLS,
                    it.NATURAL
                ]
                if item_type in weapons:
                    item_name = item.get("name")
                    item_id = item.get("id")
                    damage = item.find("damage")

                    if damage is not None: 
                        damage_value = damage.get("value")
                        item_frame = tk.Frame(canvas, borderwidth=2, relief=tk.RIDGE)
                        name_label = tk.Label(item_frame, text=item_name)
                        name_label.bind(
                            "<Button-1>",
                            lambda event, item_id=item_id:
                            self.displayItemEditor(event, item_id)
                        )
                        name_label.pack(side=tk.LEFT)
                        damage_label = tk.Label(item_frame, text=damage_value)
                        damage_label.pack(side=tk.RIGHT, anchor=tk.E)

                        canvas.create_window(
                            0, y,  # x, y
                            window=item_frame,
                            anchor=tk.NW,
                            width=230
                        )
                        self.update_idletasks()
                        y += item_frame.winfo_height()

    # display the equipped guns and other distance weapons    
    def showEquippedGuns(self, canvas):
        """ This method fills a frame with data about equipped guns
        canvas: tk.Canvas() where to display the data
        """
        # clear the frame
        canvas.delete(tk.ALL)
                
        # go for the items
        items = self.char.getItems()
        
        y = 0
        for item in items:
            if item.get("equipped", "0") == "1":
                item_type = item.get("type")
                weapons = [
                    it.PISTOLS,
                    it.REVOLVERS,
                    it.RIFLES,
                    it.SHOT_GUNS,
                    it.RIFLES_SA,
                    it.SHOT_GUNS_SA,
                    it.AUTOMATIC_PISTOLS,
                    it.AUTOMATIC_RIFLES,
                    it.MASCHINE_GUNS
                ]
                if item_type in weapons:
                    item_name = item.get("name")
                    damage = item.find("damage").get("value")

                    # retrieve the loaded round
                    chambered_item = None
                    chambers = 1
                    loaded_chambers = 0
                    ammo_tag = item.find("ammo")
                    if ammo_tag is not None: 
                        active_chamber = int(ammo_tag.get("active", "1"))
                        chambers = int(ammo_tag.get("chambers", "1"))
                        loaded_ammo = ammo_tag.get("loaded", "-1")
                        ammo_list = loaded_ammo.split()
                        chambered_id = ammo_list[active_chamber - 1]
                        chambered_item = self.char.getItemById(chambered_id)
                        for chamber in ammo_list:
                            if chamber != "-1":
                                loaded_chambers += 1

                    # get other content
                    loaded_clip = None
                    content = item.get("content", "x")
                    if content != "x":
                        content_list = content.split()
                        for content_id in content_list:
                            content_item = self.char.getItemById(content_id)
                            if content_item is not None:
                                content_type = content_item.get("type")
                                if content_type == it.CLIP:
                                    loaded_clip = content_item

                    # building the display ...
                    item_id = item.get("id")
                    weapon_frame = tk.Frame(
                        canvas,
                        borderwidth=2,
                        relief=tk.RIDGE
                    )
                    name_line = tk.Frame(weapon_frame)
                    name_label = tk.Label(
                        name_line,
                        text=item_name,
                        justify=tk.LEFT
                    )
                    name_label.bind(
                        "<Button-1>",
                        lambda event, item_id=item_id:
                            self.displayItemEditor(event, item_id))
                    name_label.pack(side=tk.LEFT, fill=tk.X, expand=1)
                    chambered_line = tk.Frame(weapon_frame)
                    if chambered_item is None:
                        damage_label = tk.Label(name_line, text=damage)
                        damage_label.pack(side=tk.RIGHT, anchor=tk.E)
                        chamber_label = tk.Label(
                            chambered_line,
                            text=msg.ES_NOT_LOADED
                        )
                        chamber_label.pack()
                    else: 
                        chambered_name = chambered_item.get("name")
                        damage = chambered_item.find("damage").get("value")
                        chamber_label = tk.Label(
                            chambered_line,
                            text=chambered_name
                        )
                        chamber_label.pack(side=tk.LEFT, fill=tk.X, anchor=tk.W)
                        damage_label = tk.Label(chambered_line, text=damage)
                        damage_label.pack(side=tk.RIGHT, anchor=tk.E)
                    ammo_line = tk.Frame(weapon_frame)
                    if loaded_clip is None:
                        ammo_text = msg.ES_CHAMBERED_AMMO.format(
                            chambers=chambers,
                            loaded=loaded_chambers
                        )
                        ammo_label = tk.Label(ammo_line, text=ammo_text)
                        ammo_label.pack(fill=tk.X, expand=1)
                    else:
                        clip_name = loaded_clip.get("name")
                        clip_size = loaded_clip.find("container").get("size")
                        clip_content = loaded_clip.get("content", "x").split()
                        ammo_in_clip = 0
                        if len(clip_content) == 1 and clip_content[0] == "x":
                            pass
                        else:
                            ammo_in_clip = len(clip_content)
                        ammo_text = msg.ES_CLIP.format(
                            name=clip_name,
                            number=ammo_in_clip,
                            capacity=clip_size
                        )
                        ammo_label = tk.Label(ammo_line, text=ammo_text)
                        ammo_label.pack(fill=tk.X, expand=1)

                    name_line.pack(fill=tk.X, expand=1)
                    chambered_line.pack(fill=tk.X, expand=1)
                    ammo_line.pack(fill=tk.X, expand=1)
                    
                    canvas.create_window(
                        0, y,  # x, y
                        window=weapon_frame,
                        anchor=tk.NW,
                        width=230
                    )
                    self.update_idletasks()
                    y += weapon_frame.winfo_height()
        
    # called when item shall be equipped
    def equipItem(self, event, item_id):
        item = self.char.getItemById(item_id)
        quantity = int(item.get("quantity"))
        if quantity > 1: 
            self.char.splitItemStack(item, quantity - 1)
        self.char.equipItem(item)
        self.updateItemList()

    # this method calculates the weight of all carried items ... 
    def updateWeight(self):
        items = self.char.getItems()
        weight = 0
        for item in items: 
            if item.get("equipped", "0") == "1":
                weight = weight + self.char.getWeight(item)
        
        weight_str = ""
        if weight > 1000:
            weight_str = str(round(weight/1000.0, 2)) + msg.ES_KG
        else:
            weight_str = str(weight) + msg.ES_G

        weight_str = msg.ES_WEIGHT + weight_str
        return weight_str

    # called when item shall be unequipped
    def unequipItem(self, event, item_id):
        item = self.char.getItemById(item_id)
        if int(self.active_bag_id) == int(item_id):
            self.active_bag_id = -1
        self.char.unequipItem(item)
        self.updateItemList()

    # pack an item into the active bag
    def packItem(self, event, item_id):
        item = self.char.getItemById(str(item_id))
        bag = self.char.getItemById(str(self.active_bag_id))
        if bag is not None:
            self.char.packItem(item, bag)
            self.updateItemList()

    # unpack the given item from its bag
    def unpackItem(self, event, item_id):
        item = self.char.getItemById(str(item_id))
        self.char.unpackItem(item)
        self.updateItemList()

    # set the item as active bag
    def setActiveBag(self, event, item_id):
        self.active_bag_id = int(item_id)
        self.showEquippedItems()

    # open an item editor
    def displayItemEditor(self, event, item_id):
        item = self.char.getItemById(item_id)
        
        # check if an itemeditor is currently open ... 
        if self.app.open_windows["itemedit"] != 0:
            open_id = self.app.open_windows["itemedit"].itemId()
            
            # focus if it is the same item 
            if open_id == item_id:
                self.app.open_windows["itemedit"].focus()

            # or close and open a new one ...
            else:
                self.app.open_windows["itemedit"].close()
                self.app.open_windows["itemedit"] = ItemEditor(self, item)
        
        # or open a new window ... 
        else:
            self.app.open_windows["itemedit"] = ItemEditor(self, item)
