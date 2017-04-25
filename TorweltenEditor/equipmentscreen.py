# coding=utf-8
import tk_ as tk
from PIL import ImageTk
from tooltip import ToolTip
from itemeditor import ItemEditor
from inventoryeditor import InventoryEditor
import config

it = config.ItemTypes()
msg = config.Messages()
colors = config.Colors()


class EquipmentScreen(tk.Frame):
    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.char = app.char
        self.itemlist = app.itemlist

        self.canvas_width = 0

        self.account_info = tk.StringVar()

        self.active_bag_id = -1
        self.open_windows = app.open_windows

        # define the three columns
        self.left_frame = tk.Frame(self)
        self.left_frame.place(
            relx=0,
            rely=0,
            relwidth=1/3,
            relheight=1,
            anchor=tk.NW
        )

        # displaying the characters initial account
        self.initial_account_frame = self.initialAccount(self.left_frame)
        self.initial_account_frame.pack(fill=tk.X)

        self.updateInitialAccount()

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
            font=config.Style.TITLE_LF_FONT
        )
        self.equipped_canvas = tk.Canvas(
            self.equipped_frame,
            width=1,
            height=1
        )
        self.equipped_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
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
        self.equipped_frame.pack(fill=tk.BOTH, expand=1)
        self.showEquippedItems()

        # center frame
        # used for the weapons
        self.center_frame = tk.Frame(self)
        self.melee_frame = tk.LabelFrame(
            self.center_frame,
            text=msg.ES_MELEE,
            font=config.Style.TITLE_LF_FONT
        )
        self.melee_canvas = tk.Canvas(
            self.melee_frame,
            width=1,
            height=1
        )
        self.melee_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
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
        self.melee_frame.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=.5,
            anchor=tk.NW
        )

        self.guns_frame = tk.LabelFrame(
            self.center_frame,
            text=msg.ES_GUNS,
            font=config.Style.TITLE_LF_FONT
        )
        self.guns_canvas = tk.Canvas(
            self.guns_frame,
            width=1,
            height=1
        )
        self.guns_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
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

        self.guns_frame.place(
            relx=0,
            rely=0.5,
            relwidth=1,
            relheight=.5,
            anchor=tk.NW
        )
        self.center_frame.place(
            relx=1/3,
            rely=0,
            relwidth=1/3,
            relheight=1,
            anchor=tk.NW
        )
        self.showEquippedGuns(self.guns_canvas)
        self.showEquippedMelee(self.melee_canvas)
        
        # the right frame is used for unassigned items
        self.right_frame = tk.Frame(self)
        self.unassigned_frame = tk.LabelFrame(
            self.right_frame,
            text=msg.ES_UNASSIGNED,
            font=config.Style.TITLE_LF_FONT
        )
        self.unassigned_canvas = tk.Canvas(
            self.unassigned_frame,
            height=1,
            width=1
        )
        self.unassigned_canvas.bind("<Configure>", self.updateItemList)
        self.unassigned_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
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
        self.unassigned_frame.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1,
            anchor=tk.NW
        )
        self.right_frame.place(
            relx=2/3,
            rely=0,
            relwidth=1/3,
            relheight=1,
            anchor=tk.NW
        )
        self.showUnassignedItems()

    # handling the initial account ... 
    def initialAccount(self, parent):
        frame = tk.Frame(parent)
        frame.columnconfigure(1, weight=100)

        minus = ImageTk.PhotoImage(file="img/minus.png")
        reduce_account = tk.Button(
            frame,
            image=minus,
            command=lambda: self.updateInitialAccount(-1)
        )
        reduce_account.image = minus

        img = ImageTk.PhotoImage(file="img/money.png")
        account_label = tk.Label(
            frame,
            textvariable=self.account_info,
            compound = tk.LEFT,
            image=img,
        )
        account_label.image = img
        account_label.grid(row=0, column=1)

        plus = ImageTk.PhotoImage(file="img/plus.png")
        increase_account = tk.Button(
            frame,
            image=plus,
            command=lambda: self.updateInitialAccount(+1)
        )
        increase_account.image = plus

        mode = self.char.getEditMode()
        if mode == "generation":
            reduce_account.grid(row=0, column=0)
            increase_account.grid(row=0, column=2)

        return frame

    def updateInitialAccount(self, change=0):
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

        if new_value < 0:
            return

        # update the account and xp ..
        if change != 0:
            self.char.updateAvailableXP(-change)
            self.char.updateAccount(change*1000, reason=msg.CHAR_STARTING_CAPITAL)
        account.set("initial", str(new_value))

        # display the value ...
        initial_amount = 1000 * new_value
        text = msg.ES_INITIAL_FUNDS.format(amount=str(initial_amount))
        self.account_info.set(text)

    # open the inventory editor and add it to the list of the open windows
    def displayInventoryEditor(self):
        if self.open_windows["inv"] != 0:
            self.open_windows["inv"].focus()
        else:
            self.open_windows["inv"] = InventoryEditor(self)
            self.open_windows["inv"].focus()

    # called when something has changed and the item lists need updating ...
    def updateItemList(self, event=None):
        if event:
            self.canvas_width = event.width
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
        canvas.update()

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
                amount_label.grid(row=0, column=0, sticky=tk.EW)
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
                name_label.grid(row=0, column=1, sticky=tk.EW)
                item_type = item.get("type")
                if item_type in equippable_types:
                    show = True
                    if item_type == it.TOOLS:
                        container = item.find("container")
                        damage = item.find("damage")
                        if damage is None and container is None:
                            show = False

                    equip_icon = ImageTk.PhotoImage(file="img/equip.png")
                    equip_button = tk.Button(item_frame, image=equip_icon)
                    ToolTip(equip_button, msg.ES_TT_EQUIP)
                    equip_button.image = equip_icon
                    equip_button.bind(
                        "<Button-1>",
                        lambda event, item_id=item_id:
                            self.equipItem(event, item_id)
                    )
                    if show:
                        equip_button.grid(row=0, column=2, sticky=tk.EW)
                    else:
                        empty = tk.Label(item_frame, text=" ", width=2)
                        empty.grid(row=0, column=2)
                else:
                    empty = tk.Label(item_frame, text=" ", width=2)
                    empty.grid(row=0, column=2, sticky=tk.EW)
                    
                if self.active_bag_id >= 0:
                    pack_icon = ImageTk.PhotoImage(file="img/pack.png")
                    pack_button = tk.Button(item_frame, image=pack_icon)
                    ToolTip(pack_button, msg.ES_TT_PACK)
                    pack_button.image = pack_icon
                    pack_button.bind(
                        "<Button-1>",
                        lambda event, item_id=item_id:
                            self.packItem(event, item_id))
                    pack_button.grid(row=0, column=3, sticky=tk.EW)
                else:
                    empty = tk.Label(item_frame, text=" ", width=2)
                    empty.grid(row=0, column=3, sticky=tk.EW)
                
                canvas.create_window(
                    0, y,  # x, y
                    width=self.canvas_width,
                    window=item_frame,
                    anchor=tk.NW,
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
            width=self.canvas_width
        )
        lines = self.showEquippedClothing(armor_frame)
        if lines > 1:
            armor = canvas.create_window(
                0, y,  # x, y
                window=armor_frame,
                anchor=tk.NW,
                width=self.canvas_width
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
                width = self.canvas_width
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
                width=self.canvas_width
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
            bag_frame.config(
                font=config.Style.BAG_LF_FONT,
            )
            ToolTip(bag_frame, msg.ES_TT_ACTIVE_BAG)
        else:
            ToolTip(bag_frame, msg.ES_TT_INACTIVE_BAG)

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
                    unpack_icon = ImageTk.PhotoImage(file="img/unpack.png")
                    item_unpack = tk.Button(item_line, image=unpack_icon)
                    ToolTip(item_unpack, msg.ES_TT_UNPACK)
                    item_unpack.image = unpack_icon
                    item_unpack.bind(
                        "<Button-1>",
                        lambda event, id=item_id:
                            self.unpackItem(event, id)
                    )
                    item_unpack.pack(side=tk.RIGHT, anchor=tk.E)
                    item_line.pack(fill=tk.X, expand=1)

        children = bag_frame.winfo_children()
        # for empty bag ...
        if not children:
            tk.Label(bag_frame, text=" ").pack()

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
        frame.columnconfigure(0, weight=100)
        name_label = tk.Label(frame, text=msg.ES_ITEMNAME)
        name_label.grid(row=row, column=0, sticky=tk.W)
        sd_label = tk.Label(frame, text=msg.ES_DAMAGE_S)
        sd_label.grid(row=row, column=1, sticky=tk.EW)
        qual_label = tk.Label(frame, text=msg.ES_QUALITY_S)
        qual_label.grid(row=row, column=2, sticky=tk.EW)
        row = 1
        clothing_and_bags = [
            it.CLOTHING,
            it.ARMOR,
            it.HARNESS,
            it.BAG,
            it.CONTAINER,
            it.TOOLS
        ]

        for item in items:
            if (item.get("equipped", "0") == "1" and
                item.get("type") in clothing_and_bags
            ):
                # only show tools that are containers ...
                if item.get("type") == it.TOOLS:
                    container = item.find("container")
                    if container is None:
                        continue
                name = item.get("name")
                item_id = item.get("id")
                name_label = tk.Label(frame, text=name)
                name_label.bind(
                    "<Button-1>",
                    lambda event, item_id=item_id:
                        self.displayItemEditor(event, item_id)
                )
                name_label.grid(row=row, column=0, sticky=tk.W)
                sd = ""
                damage = item.find("damage")
                if damage is not None:
                    sd = damage.get("value", "")
                sd_label = tk.Label(frame, text=sd)
                sd_label.grid(row=row, column=1, sticky=tk.EW)
                quality = item.get("quality")
                qual_label = tk.Label(frame, text=quality)
                qual_label.grid(row=row, column=2, sticky=tk.EW)
                unequip_icon = ImageTk.PhotoImage(file="img/unequip.png")
                unequip_button = tk.Button(frame, image=unequip_icon)
                ToolTip(unequip_button, msg.ES_TT_UNEQUIP)
                unequip_button.image = unequip_icon
                item_id = item.get("id")
                unequip_button.bind(
                    "<Button-1>", lambda event, item_id=item_id:
                        self.unequipItem(event, item_id)
                )
                unequip_button.grid(row=row, column=3, sticky=tk.EW)
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
                    it.CLUB,
                    it.BLADE,
                    it.STAFF,
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
                            width=self.canvas_width
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
                    it.PISTOL,
                    it.REVOLVER,
                    it.RIFLE,
                    it.SHOT_GUN,
                    it.RIFLE_SA,
                    it.SHOT_GUN_SA,
                    it.AUTOMATIC_WEAPON,
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
                        width=self.canvas_width
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
