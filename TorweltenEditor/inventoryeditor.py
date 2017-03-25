import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk
import xml.etree.ElementTree as et
import config
import random
from tooltip import ToolTip

msg = config.Messages()
val = config.Values()
it = config.ItemTypes()


class InventoryEditor(tk.Toplevel):
    """ This class creates an inventory shop to add items to the inventory

    main (EquipmentScreen): the program module using this window
    """

    def __init__(self, main):
        tk.Toplevel.__init__(self)
        # get the data from the application
        self.char = main.char
        self.itemlist = main.itemlist
        self.main = main

        self.items = self.itemlist.getAllItems()
        self.cur_selection = 0
        
        # prepare variables for the item
        self.item = 0
        self.new_item = et.Element("item")
        self.item_data = {}
        self.item_data_trace = {}
        self.item_desc_edited = False

        # costruct the window
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title(msg.IE_TITLE)
        self.frame = tk.Frame(self)

        self.selection_frame = tk.Frame(self.frame)
        self.selection_frame.pack(side=tk.LEFT, fill=tk.Y, expand=1)
        
        self.main_display = tk.Frame(self.frame)

        self.toolbar = tk.Frame(self.selection_frame)
        self.toolbar.pack(fill=tk.X, expand=1)

        self.selector_list_frame = tk.Frame(self.selection_frame)
        self.selector_list = ttk.Treeview(
            self.selector_list_frame,
            selectmode=tk.BROWSE,
            show="tree",
            height=20
        )
        self.selector_list.bind("<<TreeviewSelect>>", self.selectionChanged)
        self.selector_scroll = tk.Scrollbar(
            self.selector_list_frame,
            orient=tk.VERTICAL,
            command=self.selector_list.yview
        )
        self.selector_list.config(yscrollcommand=self.selector_scroll.set)
        self.selector_scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=1)
        self.selector_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.selector_list_frame.pack(
            fill=tk.Y,
            expand=1,
            anchor=tk.W
        )
        self.selector_list.focus()

        self.item_frame = tk.Frame(self.main_display)
        self.item_title_frame = tk.Frame(self.item_frame)
        self.item_title = tk.Label(
            self.item_title_frame,
            font="Arial 16 bold",
            text=msg.ITEMNAME,
            justify=tk.LEFT
        )
        self.item_title.pack(side=tk.LEFT, fill=tk.X, anchor=tk.W)
        self.item_avail = tk.Label(
            self.item_title_frame,
            font="Arial 16 bold",
            text=msg.IE_AVAIL_S
        )
        self.item_avail.pack(side=tk.RIGHT, anchor=tk.E)
        self.item_price = tk.Label(
            self.item_title_frame,
            font="Arial 16 bold",
            text=msg.IE_COST
        )
        self.item_price.pack(side=tk.RIGHT, anchor=tk.E)
        self.item_title_frame.pack(
            side=tk.TOP, anchor=tk.NW, fill=tk.X)
        self.item_info_text = tk.Text(
            self.item_frame, width=70, height=12, wrap=tk.WORD
        )
        self.item_info_text.bind("<BackSpace>", self.descriptionEdited)
        self.item_info_text.bind("<Delete>", self.descriptionEdited)
        self.item_info_text.bind("<space>", self.descriptionEdited)
        self.item_info_text.pack()
        self.item_add_frame = tk.Frame(self.item_frame)
        
        self.item_add_frame.pack()
        self.item_frame.pack(side=tk.LEFT)

        self.main_display.pack(fill=tk.BOTH, expand=1, anchor=tk.W)

        self.frame.pack(fill=tk.BOTH, expand=1)

        # reserved for sub_modules ...
        self.sub_module = tk.Frame(self.main_display)

        self.displayModules()
        self.displayItems()

    def _clearList(self):
        current = self.selector_list.get_children()
        self.selector_list.delete(*current)

    def displayItems(self):
        self.sub_module.pack_forget()
        self.item_frame.pack()

        self._clearList()

        nodes = {}
        groups = self.itemlist.getGroups()

        for group in groups:
            group_id = group.get("id", "0")
            parent_id = group.get("parent", "")
            parent = nodes.get(parent_id, "")
            nodes[group_id] = self.selector_list.insert(
                parent,
                1000,
                text=group.get("name","...")
            )

        for item in self.items:
            parent_id = item.get("parent", "")
            parent = nodes.get(parent_id, "")
            self.selector_list.insert(
                parent,
                1000,
                text=item.get("name")
            )

    def displayModules(self):
        list_icon = ImageTk.PhotoImage(file="img/tree_list.png")
        item_list = tk.Button(
            self.toolbar,
            text="Liste",
            image=list_icon,
            command=self.displayItems
        )
        item_list.image=list_icon
        item_list.pack(side=tk.LEFT)
        shirt_icon = ImageTk.PhotoImage(file="img/jacket.png")
        clothing = tk.Button(
            self.toolbar,
            text="Cloth",
            image=shirt_icon,
            command=self.customClothing
        )
        clothing.image=shirt_icon
        clothing.pack(side=tk.LEFT)

    def selectionChanged(self, event=None):
        """ Checks if the selected item needs to be changed

        Args:
            event (unused): passed from the .bind()
        """

        selection = self.selector_list.selection()
        if self.cur_selection != self.selector_list.item(selection):
            self.displayItem()

    def displayItem(self):
        selection = self.selector_list.selection()
        # do not remove item if selection is just unselected ...
        if not selection:
            return

        selected_name = self.selector_list.item(selection).get("text")

        # is it an item or a group`?
        for item in self.items:
            if item.get("name") == selected_name:
                break
        else:
            return

        # clear the add item frame
        widgets = self.item_add_frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        self.item_desc_edited = False

        self.cur_selection = selection

        # create the new item (as we do not want to change our item list)
        new_item = et.Element("item")
        new_item.set("name", selected_name)
        new_item.set("weight", item.get("weight", "0"))
        new_item.set("type", item.get("type", it.GENERIC))
        self.item = item
        self.new_item = new_item
        
        # transfer basic tags ...
        damage = self.item.find("damage") 
        if damage is not None:
            new_item.append(damage)
        container = self.item.find("container")
        if container is not None:
            new_item.append(container)
        ammo = self.item.find("ammo")
        if ammo is not None:
            new_item.append(ammo)
        
        # set initial price        
        price = float(item.get("price"))
        self.setPrice(price)

        # update the info ...
        self.item_title.config(text=selected_name)
        description = item.find("description")

        # add the text    
        if description is not None:
            self.setDescription(description)
        else: 
            self.item_info_text.delete("1.0", tk.END)
            
        # add selectors for quantity, quality and other options stuff ... 
        options = item.findall("option")
        for option in options:
            option_name = option.get("name")
            self.item_data[option_name] = tk.StringVar()
            self.item_data[option_name].trace("w", self.variable_changed)
            self.item_data_trace[str(self.item_data[option_name])] = option_name

            # are there values???
            option_values = option.get("values")
            
            option_text = tk.Label(self.item_add_frame, text=option_name)
            option_text.pack(side=tk.LEFT)

            option_widget = tk.Entry(
                self.item_add_frame,
                width=15,
                textvariable=self.item_data[option_name]
            )
            if option_values:
                option_values = option_values.split(",")
                self.item_data[option_name].set(option_values[0])
                option_widget = tk.OptionMenu(
                    self.item_add_frame,
                    self.item_data[option_name],
                    *option_values)
            option_widget.pack(side=tk.LEFT)

        # add quantity scroller
        self.item_data["quantity"] = tk.StringVar()
        self.item_data["quantity"].trace("w", self.variable_changed)
        self.item_data_trace[str(self.item_data["quantity"])] = "quantity"

        self.item_data["quantity"].set(1)
        quantity_text = tk.Label(self.item_add_frame, text=msg.IE_QUANTITY)
        quantity_text.pack(side=tk.LEFT)
        quantity_scroller = tk.Spinbox(
            self.item_add_frame,
            textvariable=self.item_data["quantity"],
            width=3
        )
        # is there a standard quantity info on the item?
        packs = item.findall("./pack")
        packs_values = []
        widget_width = 0
        for pack in packs:
            pack_name = pack.get("name")
            packs_values.append(pack_name)
            if len(pack_name) > widget_width:
                widget_width = len(pack_name)
        if len(packs_values) > 0:
            quantity_scroller.config(values=packs_values, width=widget_width)
        else:
            quantity_scroller.config(from_=1, to=100)
        quantity_scroller.pack(side=tk.LEFT)

        # check for minimum and maximum quality
        min_qual = self.getMinQuality()
        max_qual = self.getMaxQuality()
        base_qual = 6
        if base_qual < min_qual:
            base_qual = min_qual
        if base_qual > max_qual:
            base_qual = max_qual
        self.item_data["quality"] = tk.StringVar()
        self.item_data["quality"].set(base_qual)
        self.item_data["quality"].trace("w", self.variable_changed)
        self.item_data_trace[str(self.item_data["quality"])] = "quality"
        quality_text = tk.Label(self.item_add_frame, text=msg.IE_QUALITY)
        quality_text.pack(side=tk.LEFT)
        quality_scroller = tk.Spinbox(
            self.item_add_frame,
            from_=min_qual,
            to=max_qual,
            textvariable=self.item_data["quality"],
            width=3)
        quality_scroller.pack(side=tk.LEFT)

        # set the starting quality
        self.new_item.set("quality", str(base_qual))

        # adding the button to add the item
        button = tk.Button(
            self.item_add_frame,
            text=msg.IE_BUY,
            command=self.addItem
        )
        button.pack(side=tk.LEFT)

    def setText(self):
        current_content = self.item_info_text.get("1.0", tk.END)
        description = et.Element("description")
        description.text = current_content
        self.new_item.append(description)
            
    # Displays the description of the item 
    def setDescription(self, description):
        """ Setting the description
        Updates self.item_info_text a tk.Text widget
        description: et.Element (intended to handle <description>
        displays content from <text> childnodes
        return: INT - length of text
        """
        # clear the widget
        self.item_info_text.delete("1.0", tk.END)

        # add text that is without <text> tag ...
        if description.text is not None:
            self.item_info_text.insert(tk.END, description.text)

    # set the price of the item to a new value
    def setPrice(self, value):
        """ updates the price of self.new_item
        (et.Element) and self.item_price (tk.Label)
        value: FLOAT [STRING (if valid . or , separated number)
        or INT will be transformed if]
        """
        
        text_value = msg.IE_PRICE + ": "
        float_value = 0.0

        if type(value) == str:
            if "." in value:
                value = value.split(".")
            elif "," in value:
                value = value.split(",")
            else:
                value = [value, "00"]
            
            # raise a value error if the string
            # can't be transformed to a number!
            try: 
                test = int(value[1])
            except ValueError:
                error = "Input string needs to be a number: 0.00 or 0,00"
                raise ValueError(error)
            else: 
                if test < 0:
                    error = "Input string needs to be a number: 0.00 or 0,00"
                    raise ValueError(error)

            if len(value[1]) > 2:
                value[1] = value[1][:2]
            float_value = float(value[0] + "." + value[1])
            text_value = text_value + value[0] + "," + value[1]
        elif type(value) == int:
            float_value = float(value)
            text_value = text_value + str(value) + ",00"
        elif type(value) == float:
            value = round(value, 2)
            float_value = value
            value = str(value).split(".")
            if len(value[1]) == 1:
                value[1] += "0"
            elif len(value[1]) > 2:
                value[1] = value[1][:2]
            text_value = text_value + value[0] + "," + value[1]
        else: 
            in_type = type(value).__name__.upper()
            error = "Input was " + in_type + " needs to be FLOAT, INT or STR"
            raise TypeError(error)

        self.item_price.config(text=text_value)
        self.new_item.set("price", str(float_value))

    # get the price of an item
    def getPrice(self):
        """
        retrieve the stored value from the Element self.new_item
        return: FLOAT
        """
        price = float(self.new_item.get("price", "1"))
        return price

    # trace the variables
    def variable_changed(self, name, e, m):
        """
        this method traces the variable changes of an item ...
        tcl_var: STRING tcl name of the passing variable
        empty: is an empty string
        mode: STRING: w or r
        """
        changed = self.item_data_trace[name]
        value = self.item_data[changed].get()

        if changed == "quantity":
            self.quantityChanged(value)
        elif changed == "quality":
            self.qualityChanged(value)
        else:
            # write the selected option into the new item
            element = self.new_item.find("option[@name='"+changed+"']")
            if element is None:
                element = et.Element("option")
                element.set("name", changed)
                self.new_item.append(element)
            
            element = self.new_item.find("option[@name='"+changed+"']")
            element.set("value", str(value))

            # now we have to find out if the selected option changes more
            # get the option of the item
            option = self.item.find("option[@name='"+changed+"']") 
            
            # find out if there is a tag which is modified
            tag_name = option.get("tag") 
            tag = None
            if tag_name:
                tag = self.item.find(tag_name+"[@name='"+value+"']")
            if tag is not None:
                old_tag = self.new_item.find("./"+tag_name)
                self.new_item.remove(old_tag)
                self.new_item.append(tag)

            # find out if this option modifies an attribute
            # (price, weight, avail) these are stores as space
            # separeted tuples (price:20 weight:20 ...)
            attrib = option.get("attrib")
            if attrib is not None:
                attrib_list = attrib.split()
                for attrib_tuple in attrib_list: 
                    elements = attrib_tuple.split(":")
                    name = elements[0]
                    value = elements[1]
                    self.item.set(name, value)
                    # make adjustments based on the quality
                    if name == "price" or name == "avail":
                        qualtity = self.item.get("quality", "7")
                        self.qualityChanged(qualtity, direct=True)

    # trace the variable for the item quantity    
    def quantityChanged(self, quantity):
        """
        handle the quantity changed 
        quantity: STRING (can be a pack name)
        """
        
        # check if the item has packs ...
        packs = self.item.findall("pack")
        for pack in packs:
            if pack.get("name") == quantity:
                quantity = int(pack.get("quantity"))
                break

        try:
            quantity = int(quantity)
        except ValueError: 
            quantity = 1
            self.item_data["quantity"].set(quantity)
        
        old_quantity = self.new_item.get("quantity", "1")
        self.new_item.set("quantity", str(quantity))
        
        # update price
        old_price = self.getPrice() / int(old_quantity) 
        new_price = old_price * quantity
        self.setPrice(new_price)

    # the quality has been changed
    def qualityChanged(self, value, direct=False):
        """
        handling changes of the qualtity selector
        value: STRING (will be stripped to a INT range 3:9)
        """    
        # #cleaning the value!
        try:
            value = int(value)
        except ValueError:
            value = 6

        min_qual = self.getMinQuality()
        max_qual = self.getMaxQuality()
        if value > max_qual:
            value = max_qual
        if value < min_qual:
            value = min_qual
        
        # the quality matrix
        quality = {
            3: [0.1, 2, msg.IE_QUALITY_3],
            4: [0.25, 1, msg.IE_QUALITY_4],
            5: [0.5, -1, msg.IE_QUALITY_5],
            6: [1.0, 0, msg.IE_QUALITY_6],
            7: [1.5, 1, msg.IE_QUALITY_7],
            8: [2.5, 3, msg.IE_QUALITY_8],
            9: [5.0, 4, msg.IE_QUALITY_9]
        }        
        
        old_quality = int(self.new_item.get("quality", "6"))
        old_price = self.getPrice() / quality[old_quality][0]
        
        # don't adjust for former quality 
        if direct: 
            old_price = self.getPrice()

        new_price = old_price * quality[value][0]
        self.new_item.set("quality", str(value))
        self.setPrice(new_price)

    # check if a item has a minimal quality
    def getMinQuality(self):
        """
        retrieve the minimal quality of an item or the standard minimum
        return: INT range 3-9
        """
        # begin with the standard value
        min_quality = 3

        # try reading the value from the item
        quality = self.item.get("quality")
        if quality:
            quality = quality.split(" ")
            min_quality = quality[0]

        return int(min_quality)

    def getMaxQuality(self):
        """
        retrieve the maximum quality of an item or the standard maximum
        return: INT range 3-9
        """
        # begin with the standard value
        max_quality = 9

        # try reading the value from the item
        quality = self.item.get("quality")
        if quality:
            quality = quality.split(" ")
            if len(quality) == 2:
                max_quality = quality[1]
            else:
                max_quality = quality[0]

        return int(max_quality)

    # the user changed the description
    def descriptionEdited(self, event):
        self.item_desc_edited = True

    def addItem(self, text=True):
        if text:
            self.setText()

        # add the item
        self.char.addItem(self.new_item)
        self.main.updateItemList()
        # show again, to make sure a new item is generated ...
        self.selector_list.selection_set(self.cur_selection)
        self.displayItem()

    def customItem(self, event):
        """ Creating a new custom item 
        
        event (unused) called by a click event
        
        """
        
        # hiding the standard item frame 
        self._clearList()
        self.item_frame.pack_forget()

        # clear the sub_module frame
        widgets = self.sub_module.winfo_children()
        for widget in widgets:
            widget.destroy()

        custom_item = CustomItem(self.sub_module, self.main)
        custom_item.pack(fill=tk.BOTH)
        self.sub_module.pack(side=tk.RIGHT)

    def customClothing(self):
        """ Creating a new custom clothing item

        event (unused) called by a click event

        """

        # hiding the standard item frame
        self._clearList()
        self.item_frame.pack_forget()

        # clear the sub_module frame
        widgets = self.sub_module.winfo_children()
        for widget in widgets:
            widget.destroy()

        custom_clothing = CustomClothing(self.sub_module, self.main)
        custom_clothing.pack(fill=tk.BOTH)
        self.sub_module.pack(side=tk.RIGHT)

    def displayItemFrame(self):
        self.sub_module.pack_forget()
        self.item_frame.pack(side=tk.RIGHT)

    def showTooltip(self, event, caller):
        """ Displaying tool tips"""

        infos = {
            "name": msg.IE_TT_NAME,
            "quantity": msg.IE_TT_QUANTITY,
            "quality": msg.IE_TT_QUALITY,
            "price": msg.IE_TT_PRICE,
            "weight": msg.IE_TT_WEIGHT,
            "avail": msg.IE_TT_AVAIL,
            "damage": msg.IE_TT_DAMAGE,
            "caliber": msg.IE_TT_CALIBER,
            "container": msg.IE_TT_CONTAINER
        }

        ToolTip(
            self.winfo_toplevel(),
            event=event,
            message=infos[caller]
        )

    def close(self):
        self.main.open_windows["inv"] = 0
        self.destroy()


class CustomItem(tk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent)

        self.char = main.char
        self.main = main

        self.item_data = {}
        self.item_data_trace = {}

        # building the screen an setting up variables to hold the
        # given data ...
        name_var = tk.StringVar()
        self.item_data["name"] = name_var
        top_frame = tk.Frame(main.sub_module)
        name_frame = tk.LabelFrame(top_frame, text=msg.IE_NAME)
        tk.Entry(
            name_frame,
            width=40,
            textvariable=name_var
        ).pack()
        name_frame.pack(side=tk.LEFT)
        name_frame.bind("<Enter>", lambda e: self.showTooltip(e, "name"))

        quantity_var = tk.StringVar()
        quantity_var.set("1")
        self.item_data["quantity"] = quantity_var
        quantity_frame = tk.LabelFrame(top_frame, text=msg.IE_QUANTITY)
        tk.Entry(
            quantity_frame,
            width=7,
            textvariable=quantity_var
        ).pack(fill=tk.X)
        quantity_frame.pack(side=tk.LEFT)
        quantity_frame.bind("<Enter>", lambda e: self.showTooltip(e, "quantity"))

        price_var = tk.StringVar()
        self.item_data["price"] = price_var
        price_frame = tk.LabelFrame(top_frame, text=msg.IE_PRICE)
        tk.Entry(
            price_frame,
            width=7,
            textvariable=price_var
        ).pack(fill=tk.X)
        price_frame.pack(side=tk.LEFT)
        price_frame.bind("<Enter>", lambda e: self.showTooltip(e, "price"))

        weight_var = tk.StringVar()
        self.item_data["weight"] = weight_var
        weight_frame = tk.LabelFrame(top_frame, text=msg.IE_WEIGHT)
        tk.Entry(
            weight_frame,
            width=7,
            textvariable=weight_var
        ).pack(fill=tk.X)
        weight_frame.pack(side=tk.LEFT)
        weight_frame.bind("<Enter>", lambda e: self.showTooltip(e, "weight"))

        quality_var = tk.StringVar()
        quality_var.set("6")
        self.item_data["quality"] = quality_var
        quality_frame = tk.LabelFrame(top_frame, text=msg.IE_QUALITY_S)
        tk.Entry(
            quality_frame,
            width=7,
            textvariable=quality_var
        ).pack(fill=tk.X)
        quality_frame.pack(side=tk.LEFT)
        quality_frame.bind("<Enter>", lambda e: self.showTooltip(e, "quality"))

        avail_var = tk.StringVar()
        avail_var.set("0")
        self.item_data["avail"] = avail_var
        avail_frame = tk.LabelFrame(top_frame, text=msg.IE_AVAIL_S)
        tk.Entry(
            avail_frame,
            width=7,
            textvariable=avail_var
        ).pack(fill=tk.X)
        avail_frame.pack(side=tk.LEFT)
        avail_frame.bind("<Enter>", lambda e: self.showTooltip(e, "avail"))
        top_frame.pack()

        damage_frame = tk.LabelFrame(main.sub_module, text=msg.IE_DAMAGE_HEADER)
        damage_var = tk.StringVar()
        self.item_data["damage"] = damage_var
        damage_entry = tk.Entry(damage_frame, textvariable=damage_var, width=10)
        damage_entry.pack(side=tk.LEFT)
        damage_entry.bind(
            "<Enter>",
            lambda e:
            self.showTooltip(e, "damage")
        )
        add_damage = tk.StringVar()
        self.item_data["add_damage"] = add_damage
        checkbox = tk.Checkbutton(
            damage_frame,
            text=msg.IE_USE,
            variable=add_damage,
            onvalue="1",
            offvalue="0"
        )
        checkbox.pack(side=tk.RIGHT, anchor=tk.E)
        add_damage.set("0")
        damage_frame.pack(fill=tk.X)

        caliber_frame = tk.LabelFrame(main.sub_module, text=msg.IE_CALIBER_HEAD)
        tk.Label(
            caliber_frame,
            text=msg.IE_CALIBER
        ).pack(side=tk.LEFT, anchor=tk.W)
        caliber_var = tk.StringVar()
        self.item_data["caliber"] = damage_var
        caliber_entry = tk.Entry(
            caliber_frame,
            textvariable=caliber_var,
            width=15
        )
        caliber_entry.bind(
            "<Enter>",
            lambda e:
            self.showTooltip(e, "caliber")
        )
        caliber_entry.pack(side=tk.LEFT)
        tk.Label(
            caliber_frame,
            text=msg.IE_CHAMBERS
        ).pack(side=tk.LEFT, anchor=tk.W)
        chambers_var = tk.StringVar()
        self.item_data["chambers"] = chambers_var
        chambers_entry = tk.Entry(
            caliber_frame,
            textvariable=chambers_var,
            width=5)
        chambers_entry.pack(side=tk.LEFT)

        add_caliber = tk.StringVar()
        self.item_data["add_caliber"] = add_caliber
        checkbox = tk.Checkbutton(
            caliber_frame,
            text=msg.IE_USE,
            variable=add_caliber,
            onvalue="1",
            offvalue="0"
        )
        checkbox.pack(side=tk.RIGHT, anchor=tk.E)
        add_caliber.set("0")
        caliber_frame.pack(fill=tk.X)

        container_frame = tk.LabelFrame(
            main.sub_module,
            text=msg.IE_CONTAINER
        )
        tk.Label(
            container_frame,
            text=msg.IE_NAME
        ).pack(side=tk.LEFT, anchor=tk.W)
        container_name = tk.StringVar()
        self.item_data["container"] = container_name
        container_entry = tk.Entry(
            container_frame,
            textvariable=container_name,
            width=25
        )
        container_entry.pack(side=tk.LEFT)
        container_entry.bind(
            "<Enter>",
            lambda e:
            self.showTooltip(e, "container")
        )
        add_container = tk.StringVar()
        self.item_data["add_container"] = add_container
        checkbox = tk.Checkbutton(
            container_frame,
            text=msg.IE_USE,
            variable=add_container,
            onvalue="1",
            offvalue="0"
        )
        checkbox.pack(side=tk.RIGHT, anchor=tk.E)
        add_container.set("0")
        container_frame.pack(fill=tk.X)

        text = msg.IE_DESCRIPTION
        description_frame = tk.LabelFrame(main.sub_module, text=text)
        description = tk.StringVar()
        self.item_data["description"] = description
        description_entry = tk.Entry(
            description_frame,
            textvariable=description,
            width=40
        )
        description_entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        description_frame.pack(fill=tk.X)

        itemtypes = [
            msg.IE_TYPE_CLOTHING,
            msg.IE_TYPE_MELEE,
            msg.IE_TYPE_GUNS,
            msg.IE_TYPE_CONTAINER,
            msg.IE_TYPE_TOOLS,
            msg.IE_TYPE_AMMO,
            msg.IE_TYPE_OTHER,
        ]

        type_var = tk.StringVar()
        type_var.set(msg.IE_TYPE_UNDEFINED)
        self.item_data["type"] = type_var

        tk.OptionMenu(
            main.sub_module,
            type_var,
            *itemtypes
        ).pack(fill=tk.X)

        tk.Button(
            main.sub_module,
            text=msg.IE_ADD_ITEM,
            command=self._addCustomItem
        ).pack(fill=tk.X)

        main.sub_module.pack(side=tk.RIGHT)

    def _addCustomItem(self):
        """ Building a custom item from input

        called as command on the appropriate button ...

        """

        # The data
        name = self.item_data["name"].get()
        quantity = self.item_data["quantity"].get()
        quality = self.item_data["quality"].get()
        weight = self.item_data["weight"].get()
        price = self.item_data["price"].get()
        avail = self.item_data["avail"].get()
        damage = self.item_data["damage"].get()
        add_damage = self.item_data["add_damage"].get()
        caliber = self.item_data["caliber"].get()
        chambers = self.item_data["chambers"].get()
        add_caliber = self.item_data["add_caliber"].get()
        container = self.item_data["container"].get()
        add_container = self.item_data["add_container"].get()
        item_type = self.item_data["type"].get()
        description = self.item_data["description"].get()

        # validating the user imputs ...
        valid = True

        # An item needs a name
        if len(name) < 1:
            valid = False
            self.item_data["name"].set(msg.IE_NO_NAME)

        # Quality must be integer 1 - 9
        try:
            quality = int(quality)
            if not 0 < quality <= 9:
                valid = False
                self.item_data["quality"].set(msg.IE_VALUE)
        except ValueError:
            valid = False
            self.item_data["quality"].set(msg.IE_NUMBER)

        # Quantity must be positive integer
        try:
            quantity = int(quantity)
            if not quantity > 0:
                valid = False
                self.item_data["quantity"].set(msg.IE_VALUE)
        except ValueError:
            valid = False
            self.item_data["quantity"].set(msg.IE_NUMBER)

        # Weight must be a positive integer
        try:
            weight = int(weight)
            if weight < 1:
                valid = False
                self.item_data["weight"].set(msg.IE_VALUE)
        except ValueError:
            valid = False
            self.item_data["weight"].set(msg.IE_NUMBER)

        # Price needs to be positive float
        try:
            price = price.replace(",", ".")
            price = float(price)
            if price <= 0:
                valid = False
                self.item_data["price"].set(msg.IE_VALUE)
        except ValueError:
            valid = False
            self.item_data["price"].set(msg.IE_NUMBER)

        # Availability must be integer -6 - +6
        try:
            avail = int(avail)
            if not -6 <= avail <= 6:
                valid = False
                self.item_data["avail"].set(msg.IE_VALUE)
        except ValueError:
            valid = False
            self.item_data["avail"].set(msg.IE_NUMBER)

        # let's look deeper
        # validating a damage entry
        if valid and add_damage == "1":
            try:
                damage_val = damage.split("/")
                if len(damage_val) == 2:
                    s = int(damage_val[0])
                    d = int(damage_val[1])

                    if not -9 <= s <= 9 or not -7 <= d <= 7:
                        valid = False
                        self.item_data["damage"].set(msg.IE_INVALID)
                else:
                    valid = False
                    self.item_data["damage"].set(msg.IE_INVALID)
            except ValueError:
                valid = False
                self.item_data["damage"].set(msg.IE_INVALID)

        # validating caliber entry
        if valid and add_caliber == "1":
            try:
                chambers = int(chambers)
                if not 1 <= chambers:
                    valid = False
                    self.item_data["chambers"].set(msg.IE_VALUE)
            except ValueError:
                valid = False
                self.item_data["chambers"].set(msg.IE_NUMBER)

        # making sure an item type was given
        if item_type == msg.IE_TYPE_UNDEFINED:
            valid = False

        # constructing the item ...
        if valid:
            # basics
            new_item = et.Element(
                "item",
                {"name": str(name),
                 "weight": str(weight),
                 "price": str(price),
                 "quality": str(quality),
                 "quantity": str(quantity),
                 "custom": "yes"
                 }
            )
            # clothing or armor
            if item_type == msg.IE_TYPE_CLOTHING:
                if add_damage == "1":
                    et.SubElement(
                        new_item,
                        "damage",
                        {"value": str(damage)}
                    )
                    new_item.set("type", it.ARMOR)
                else:
                    new_item.set("type", it.CLOTHING)
                if add_container == "1":
                    if container == "":
                        container = name
                    et.SubElement(
                        new_item,
                        "container",
                        {"name": str(container)}
                    )
            # any melee weapon
            elif item_type == msg.IE_TYPE_MELEE:
                if add_damage == "1":
                    et.SubElement(
                        new_item,
                        "damage",
                        {"value": str(damage)}
                    )
                    new_item.set("type", it.CLUBS)
            # any gun
            elif item_type == msg.IE_TYPE_GUNS:
                if add_damage == "1":
                    et.SubElement(
                        new_item,
                        "damage",
                        {"value": str(damage)}
                    )
                if add_caliber == "1":
                    et.SubElement(
                        new_item,
                        "ammo",
                        {"chambers": str(chambers)}
                    )
                    et.SubElement(
                        new_item,
                        "option",
                        {"name": it.OPTION_CALIBER,
                         "value": str(caliber)}
                    )
                    if chambers > 1:
                        new_item.set("type", it.REVOLVERS)
                    else:
                        new_item.set("type", it.PISTOLS)
            # any container
            elif item_type == msg.IE_TYPE_CONTAINER:
                if add_container == "1":
                    if container == "":
                        container = name
                    et.SubElement(
                        new_item,
                        "container",
                        {"name": str(container)}
                    )
                    new_item.set("type", it.CONTAINER)
                if add_caliber == "1":
                    et.SubElement(
                        new_item,
                        "option",
                        {"name": it.OPTION_CALIBER,
                         "value": str(caliber)}
                    )
                    new_item.set("type", it.CLIP)
            # any tool
            elif item_type == msg.IE_TYPE_TOOLS:
                if add_container == "1":
                    if container == "":
                        container = name
                    et.SubElement(
                        new_item,
                        "container",
                        {"name": str(container)}
                    )
                if add_damage == "1":
                    et.SubElement(
                        new_item,
                        "damage",
                        {"value": str(damage)}
                    )
                new_item.set("type", it.TOOLS)
            # ammo item
            elif item_type == msg.IE_TYPE_AMMO:
                if add_damage == "1":
                    et.SubElement(
                        new_item,
                        "damage",
                        {"value": str(damage)}
                    )
                if add_caliber == "1":
                    et.SubElement(
                        new_item,
                        "ammo",
                        {"chambers": str(chambers)}
                    )
                    et.SubElement(
                        new_item,
                        "option",
                        {"name": it.OPTION_CALIBER,
                         "value": str(caliber)}
                    )
                new_item.set("type", it.AMMO)
            # or generic item ...
            elif item_type == msg.IE_TYPE_OTHER:
                new_item.set("type", it.GENERIC)

            # adding the description
            desc = et.SubElement(new_item, "description")
            if description == "":
                description = " "
            desc.text = description
            self.new_item = new_item
            self.addItem(text=False)

    def showTooltip(self, event, caller):
        """ Displaying tool tips"""

        infos = {
            "name": msg.IE_TT_NAME,
            "quantity": msg.IE_TT_QUANTITY,
            "quality": msg.IE_TT_QUALITY,
            "price": msg.IE_TT_PRICE,
            "weight": msg.IE_TT_WEIGHT,
            "avail": msg.IE_TT_AVAIL,
            "damage": msg.IE_TT_DAMAGE,
            "caliber": msg.IE_TT_CALIBER,
            "container": msg.IE_TT_CONTAINER
        }

        ToolTip(
            self.winfo_toplevel(),
            event=event,
            message=infos[caller]
        )


class CustomClothing(tk.Frame):
    """ A submodule to generate custom clothing items

    Args:
        parent(tk.Frame): where to display
    """

    # [name, base price, area factor]
    body_parts = [
        [msg.IE_CE_HEAD, val.IE_BASE_PRICE1, val.IE_AREA_MEDIUM],
        [msg.IE_CE_NECK, val.IE_BASE_PRICE2, val.IE_AREA_SMALL],
        [msg.IE_CE_TORSO, val.IE_BASE_PRICE1, val.IE_AREA_LARGE],
        [msg.IE_CE_UPPERARMS, val.IE_BASE_PRICE2, val.IE_AREA_MEDIUM],
        [msg.IE_CE_FOREARMS, val.IE_BASE_PRICE2, val.IE_AREA_MEDIUM],
        [msg.IE_CE_HANDS, val.IE_BASE_PRICE1,val.IE_AREA_SMALL],
        [msg.IE_CE_HIPS, val.IE_BASE_PRICE1, val.IE_AREA_LARGE],
        [msg.IE_CE_UPPERLEGS, val.IE_BASE_PRICE2, val.IE_AREA_LARGE],
        [msg.IE_CE_LOWERLEGS, val.IE_BASE_PRICE2, val.IE_AREA_MEDIUM],
        [msg.IE_CE_FEET, val.IE_BASE_PRICE1, val.IE_AREA_SMALL]
    ]

    # [ name, unselected factor, selected factor, weight factor]
    elements = [
        [msg.IE_CE_CHOSEN, 0, -1, 1.0],
        [msg.IE_CE_ARMOR1, 1, val.IE_PRICE_ARMOR, 2],
        [msg.IE_CE_ARMOR2, 1, val.IE_PRICE_ARMOR, 2.5],
        [msg.IE_CE_CLOSURE, 0, 1, 1.05],
        [msg.IE_CE_COMPLEX, 0, 1, 1.25],
        [msg.IE_CE_CANVAS, 0, 1, 2.0],
        [msg.IE_CE_TRIMMINGS, 0, 1, 1.5]
    ]

    def __init__(self, parent, main):
        super().__init__(parent)

        self.char = main.char
        self.main = main

        self.item_data = {}
        self.item_data_trace = {}

        # we need to access some widgets
        self.buy = None
        self.select = None
        self.description = None
        self.trousers = None
        self.closures = None

        # core variables
        self.weight = 0
        self.avail = 0

        # building the screen an setting up variables to hold the
        # given data ...
        top_frame = self._topView(self)
        top_frame.pack(fill=tk.X, expand=1)
        middle_frame = tk.Frame(self)
        selection = self._selectionView(middle_frame)
        selection.pack(side=tk.LEFT, fill=tk.X, expand=1)
        right_frame = tk.Frame(middle_frame)
        options = self._optionsView(right_frame)
        options.pack(fill=tk.X, anchor=tk.N)
        self.buy = tk.Button(
            right_frame,
            text=msg.IE_BUY,
            state=tk.DISABLED,
            command=self._createItem
        )
        self.buy.pack(fill=tk.BOTH, expand=1)
        right_frame.pack(side=tk.LEFT, fill=tk.Y)
        middle_frame.pack(fill=tk.X)
        descripton_frame = self._descriptionView(self)
        descripton_frame.pack(fill=tk.X)

    def _topView(self, parent):
        """ Creating a frame with the name of the item """

        name_var = tk.StringVar()
        self.item_data["name"] = name_var
        name_var.trace("w", self._calculateCost)
        frame = tk.Frame(parent)
        name_frame = tk.LabelFrame(frame, text=msg.IE_NAME)
        tk.Entry(
            name_frame,
            width=40,
            textvariable=name_var
        ).pack(fill=tk.BOTH, expand=1)
        name_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        random_frame = tk.LabelFrame(frame, text=msg.IE_CE_RANDOM)
        random_button = tk.Button(
            random_frame,
            text=msg.IE_CE_GENERATE,
            command=self._generateRandom
        )
        random_button.pack(fill=tk.X)
        random_frame.pack(side=tk.LEFT)

        # name_frame.bind("<Enter>", lambda e: self.showTooltip(e, "name"))
        return frame

    def _selectionView(self, parent):
        """ creates a frame with option selection for customClothing

        Args:
            parent (tk.Frame): frame to display it in

        Note:
            uses .grid() layout
        """

        self.select = frame = tk.LabelFrame(parent, text=msg.IE_CE_SELECTION)
        frame.columnconfigure(0, weight=20)

        self._selectionHeaders(frame)

        # adding a checkbox grid for the selected options
        for row, part in enumerate(self.body_parts, start=1):
            label = tk.Label(frame, text=part[0])
            label.grid(row=row, column=0, sticky=tk.W)

            for col, el in enumerate(self.elements, start=1):
                on_value = el[2]
                if el[2] == -1:
                    on_value = part[1]
                var = tk.DoubleVar()
                var.trace("w", self._calculateCost)

                # conditional trace for trousers toggle
                legs = [msg.IE_CE_UPPERLEGS, msg.IE_CE_HIPS]
                if part[0] in legs and col == 1:
                    var.trace(
                        "w",
                        lambda n, e, v, var=var:
                            self._trousersToggle(var))

                # conditional trace for closures toggle
                core = [msg.IE_CE_TORSO, msg.IE_CE_HIPS]
                if part[0] in core and (col == 1 or col == 4):
                    var.trace("w", lambda n, e, v: self._toggleClosures())

                # conditional trace for armor toggle
                if col == 2 or col == 3:
                    var.trace("w", self._armorToggle)


                # generic variable storage for access ...
                self.item_data[part[0]+"_"+el[0]] = var
                self.item_data_trace[str(var)] = part[0]+"_"+el[0]
                var.set(el[1])
                cb = tk.Checkbutton(
                    frame,
                    var=var,
                    offvalue=el[1],
                    onvalue=on_value,
                )

                # setting the line toggle
                if col == 1:
                    cb.bind("<Button-1>", self._toggleCheckbuttons)
                if col > 1:
                    cb.config(state=tk.DISABLED)
                cb.grid(row=row, column=col)

            # adding the pockets spinboxes ...
            var = tk.StringVar()
            var.trace("w", self._calculateCost)
            handle = part[0] + "_" + msg.IE_CE_POCKETS
            self.item_data[handle] = var
            self.item_data_trace[str(var)] = handle
            pockets = tk.Spinbox(
                frame,
                textvariable=var,
                from_=0,
                to=10,
                width=2,
                state=tk.DISABLED
            )
            pockets.grid(row=row, column=col+1)

        return frame

    @staticmethod
    def _selectionHeaders(parent):
        """ adds option icons above the selection grid """

        images = [
            ImageTk.PhotoImage(file="img/ie_tick.png"),
            ImageTk.PhotoImage(file="img/ie_armor1.png"),
            ImageTk.PhotoImage(file="img/ie_armor2.png"),
            ImageTk.PhotoImage(file="img/ie_closure.png"),
            ImageTk.PhotoImage(file="img/ie_complex.png"),
            ImageTk.PhotoImage(file="img/ie_fabric.png"),
            ImageTk.PhotoImage(file="img/ie_trimmings.png"),
            ImageTk.PhotoImage(file="img/ie_pockets.png")
        ]
        for col, image in enumerate(images, start=1):
            icon = tk.Label(parent, image=image)
            icon.image = image
            icon.grid(row=0, column=col)

    def _optionsView(self, parent):
        frame = tk.Frame(parent)
        self._qualityButton(frame)
        self._fabricButton(frame)
        return frame

    def _qualityButton(self, parent):
        frame = tk.LabelFrame(parent, text=msg.IE_QUALITY)
        qualities = (
            msg.IE_QUALITY_3,
            msg.IE_QUALITY_4,
            msg.IE_QUALITY_5,
            msg.IE_QUALITY_6,
            msg.IE_QUALITY_7,
            msg.IE_QUALITY_8,
            msg.IE_QUALITY_9,
        )
        self.item_data["Q"] = var = tk.StringVar()
        var.trace("w", lambda n, e, m: self._quality(var))
        var.set(qualities[3])
        button = tk.OptionMenu(
            frame,
            var,
            *qualities
        )
        button.pack(fill=tk.X, expand=1)
        frame.pack(fill=tk.X, expand=1)

    def _fabricButton(self, parent):
        # single layer or multi layer fabric ...
        frame = tk.LabelFrame(parent, text=msg.IE_CE_FABRIC)
        layers = (
            msg.IE_CE_SINGLE_LAYER,
            msg.IE_CE_MULTI_LAYER,
            msg.IE_CE_MULTI_HEAVY
        )
        self.item_data["L"] = l_var = tk.StringVar()
        l_var.trace("w", lambda n, e, m, var=l_var: self._layers(var))
        l_var.set(layers[0])
        button = tk.OptionMenu(
            frame,
            l_var,
            *layers
        )
        button.pack(fill=tk.X, expand=1)

        # cloth quality
        fabric_group = (
            msg.IE_CE_SIMPLE,
            msg.IE_CE_ELEGANT,
            msg.IE_CE_RARE
        )
        self.item_data["F"] = f_var = tk.StringVar()
        f_var.trace("w", lambda n, e, m, var=f_var: self._fabric(var))
        f_var.set(fabric_group[0])
        button = tk.OptionMenu(
            frame,
            f_var,
            *fabric_group
        )
        button.pack(fill=tk.X, expand=1)

        # closures
        closures = (
            msg.IE_CE_NO_CLOSURE,
            msg.IE_CE_BUTTONS,
            msg.IE_CE_ZIPPER,
            msg.IE_CE_VELCRO,
            msg.IE_CE_LACING,
            msg.IE_CE_BUCKLES,
        )
        self.item_data["C"] = c_var = tk.StringVar()
        c_var.trace("w", lambda n, e, m, var=c_var: self._closures(var))
        c_var.set(closures[0])
        self.closures = tk.OptionMenu(
            frame,
            c_var,
            *closures
        )
        self.closures.config(state=tk.DISABLED)
        self.closures.pack(fill=tk.X, expand=1)

        # name of material
        subframe = tk.Frame(frame)
        tk.Label(subframe, text=msg.IE_CE_FABRIC_NAME).pack(
            side=tk.LEFT,
            expand=1,
            anchor=tk.W
        )
        self.item_data["material"] = m_var = tk.StringVar()
        tk.Entry(subframe, width=20, textvariable=m_var).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=1
        )
        subframe.pack(fill=tk.X)
        # color of clothing
        subframe = tk.Frame(frame)
        tk.Label(subframe, text=msg.IE_CE_FABRIC_COLOR).pack(
            side=tk.LEFT,
            expand=1,
            anchor=tk.W
        )
        self.item_data["color"] = c_var = tk.StringVar()
        tk.Entry(subframe, textvariable=c_var).pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=1
        )
        subframe.pack(fill=tk.X)
        # are this trousers or not?
        self.item_data["trousers"] = t_var = tk.IntVar()
        t_var.set(0)
        self.trousers = tk.Checkbutton(
            frame,
            text=msg.IE_CE_TROUSERS,
            var=t_var,
            onvalue=1,
            offvalue=0,
            state=tk.DISABLED,
            anchor=tk.W
        )
        self.trousers.pack(
            fill=tk.X,
            expand=1
        )

        frame.pack(fill=tk.X, expand=1)

    def _descriptionView(self, parent):
        self.item_data["description"] = tk.StringVar()
        frame = tk.LabelFrame(parent, text=msg.IE_DESCRIPTION)
        icon = ImageTk.PhotoImage(file="img/text_signature.png"),

        auto_describe = tk.Button(
            frame,
            image = icon,
            text = "Auto",
            compound=tk.TOP,
            command=self._autoDescription
        )
        auto_describe.image = icon
        auto_describe.pack(side=tk.LEFT, fill = tk.Y)
        self.description = tk.Text(frame, width=20, height=5, wrap=tk.WORD)
        self.description.pack(side = tk.LEFT, fill=tk.BOTH, expand=1)
        return frame

    def _armorToggle(self, name, empty, mode):
        """ .trace() for armor checkboxes in customClothing

        makes sure that armor level 1 is selected when armor level 2 is
        chosen and deselects armor level 2 once armor level 1 is deselected

        Args:
            name (str): tcl name of variable
            empty (unused)
            mode (unused)
        """

        trace = self.item_data_trace.get(name)
        clicked = self.item_data.get(trace)
        part = trace.split("_")[0]
        armor1 = self.item_data.get(part + "_" + msg.IE_CE_ARMOR1)
        armor2 = self.item_data.get(part + "_" + msg.IE_CE_ARMOR2)
        if armor1 and armor2:
            if armor1 is clicked:
                if armor1.get() == 1 and armor2.get() == 10:
                    armor2.set(1)
            if armor2 is clicked:
                if armor2.get() == 10 and armor1.get() == 1:
                    armor1.set(10)

    def _trousersToggle(self, var):
        if not self.trousers: return
        selected = var.get()
        if selected > 0:
            self.trousers.config(state=tk.NORMAL)
        else:
            self.trousers.config(state=tk.DISABLED)

    def _getSelectedOptions(self):
        body_parts = [part[0] for part in self.body_parts]
        elements = [element[0] for element in self.elements]
        elements.append(msg.IE_CE_POCKETS)
        
        selection = {}
        for part in body_parts:
            sel = elements[0]
            v_name = part + "_" + sel
            var = self.item_data.get(v_name)
            if var:
                selected = var.get()
                if selected > 0:
                    selection[part] = {}
                    for element in elements:
                        option_name = part + "_" + element
                        value = self.item_data.get(option_name).get()
                        selection[part][element] = value
        return selection

    def _selectionIterator(self, name):
        """ iterates over a specific option """
        selection = self._getSelectedOptions()
        for key in selection:
            part_data = selection[key]
            for element in part_data:
                if name in element:
                    yield part_data[element]

    def _calculateCost(self, name=None, empty=None, mode=None):
        selection = self._getSelectedOptions()
        price = 0
        for part in selection:
            base_price = selection[part][msg.IE_CE_CHOSEN]
            armor1 = selection[part][msg.IE_CE_ARMOR1]
            armor2 = selection[part][msg.IE_CE_ARMOR2]
            closure = selection[part][msg.IE_CE_CLOSURE]
            complex = selection[part][msg.IE_CE_COMPLEX]
            canvas = selection[part][msg.IE_CE_CANVAS]
            trimmings = selection[part][msg.IE_CE_TRIMMINGS]
            pockets = selection[part][msg.IE_CE_POCKETS]
            if pockets in ["", " ", "0"]:
                pockets = 0
            else:
                pockets = 1
            # calculate price
            armor = base_price * armor1 * armor2
            addon = 1 + closure + complex + canvas + trimmings + pockets
            partial_price = armor * addon
            price += partial_price

        qualities = {
            3: 0.1,
            4: 0.25,
            5: 0.5,
            6: 1.0,
            7: 1.5,
            8: 2.5,
            9: 5.0,
        }
        quality = self.item_data.get(msg.IE_QUALITY, 6)
        quality_factor = qualities[quality]
        price *= quality_factor

        fabric_factor = self.item_data.get(msg.IE_CE_FABRIC, 1)
        price *= fabric_factor

        layers_factor = self.item_data.get(msg.IE_CE_SINGLE_LAYER, 1)
        price *= layers_factor

        self.item_data[msg.IE_PRICE] = price

        if self.buy:
            price_text = msg.MONEYFORMAT % price
            price_text = price_text.replace(".", msg.MONEYSPLIT)

            text = msg.IE_BUY + "\n" + price_text
            if price > 0 and len(self.item_data["name"].get()) >= 1:
                state = tk.NORMAL
            else:
                state = tk.DISABLED
            self.buy.config(text=text, state=state)

    def _calculateWeight(self):
        selected = self._getSelectedOptions()

        armor = [msg.IE_CE_ARMOR1, msg.IE_CE_ARMOR2]
        weight_factor = 0
        for body_part in self.body_parts:
            if body_part[0] in selected.keys():
                area_factor = body_part[2]
                body_part = selected[body_part[0]]
                element_factors = 1
                for element in self.elements:
                    if ((body_part.get(element[0]) >= 1
                        and element[0] not in armor)
                        or (body_part.get(element[0]) > 1
                        and element[0] in armor)
                    ):
                        element_factors *= element[3]
                part_factor = element_factors * area_factor
                weight_factor += part_factor

        material_factor = self.item_data[msg.IE_CE_SINGLE_LAYER]
        weight = weight_factor * material_factor
        return int(weight)

    def _quality(self, var):
        qualities = {
            msg.IE_QUALITY_3: 3,
            msg.IE_QUALITY_4: 4,
            msg.IE_QUALITY_5: 5,
            msg.IE_QUALITY_6: 6,
            msg.IE_QUALITY_7: 7,
            msg.IE_QUALITY_8: 8,
            msg.IE_QUALITY_9: 9,
        }
        self.item_data[msg.IE_QUALITY] = qualities[var.get()]
        self._calculateCost()

    def _fabric(self, var):
        fabric_qualities = {
            msg.IE_CE_SIMPLE: 1,
            msg.IE_CE_ELEGANT: 2,
            msg.IE_CE_RARE: 5,
        }
        self.item_data[msg.IE_CE_FABRIC] = fabric_qualities[var.get()]
        self._calculateCost()

    def _closures(self, var):
        self.item_data[msg.IE_CE_CLOSURE] = var.get()

    def _toggleClosures(self):
        selection = self._getSelectedOptions()
        core = {msg.IE_CE_TORSO, msg.IE_CE_HIPS}.intersection(selection.keys())
        state = tk.DISABLED
        for part in core:
            if selection[part].get(msg.IE_CE_CLOSURE):
                state = tk.NORMAL
        if self.closures:
            self.closures.config(state=state)

    def _layers(self, var):
        layers = {
            msg.IE_CE_SINGLE_LAYER: 1,
            msg.IE_CE_MULTI_LAYER: 2,
            msg.IE_CE_MULTI_HEAVY: 2.5

        }
        self.item_data[msg.IE_CE_SINGLE_LAYER] = layers[var.get()]
        self._calculateCost()
        self._calculateWeight()

    def _toggleCheckbuttons(self, event):
        """ (De)activate option checkbuttons for clothing elements

        All option checkbuttons will be disabled for any given body part
        line when the select checkbutton is unchecked

        Args:
            event (tk.Event): the click on the checkbutton
        """

        row = event.widget.grid_info()["row"]
        var_name = event.widget.cget("variable")
        var_trace = self.item_data_trace[str(var_name)]
        var = self.item_data[var_trace]

        widgets = self.select.winfo_children()
        for widget in widgets:
            w_row = widget.grid_info()["row"]
            w_col = widget.grid_info()["column"]
            if w_row == row and w_col in range(2, 9):
                if var.get() == 0:
                    widget.config(state=tk.NORMAL)
                else:
                    widget.config(state=tk.DISABLED)

    def _getArmor(self):
        """ retrieve the armor selections """

        armor1 = 0
        armor2 = 0
        for armor in self._selectionIterator(msg.IE_CE_ARMOR1):
            armor1 += int(armor / 10)

        for armor in self._selectionIterator(msg.IE_CE_ARMOR2):
            armor2 += int(armor / 10)

        return armor1, armor2

    def _autoDescription(self):
        """ This generates an automatic description based on the selection"""

        text_elements = []

        clothing_names = msg.IE_CLOTHING_NAMES

        debug = ""
        for i in range(1, 8):
            key = self._getClothingKey(lookup=i)
            name, gender = clothing_names.get(key, msg.IE_CE_UNKNOWN)
            debug += "KEY: " + key + "\n"
            if name != msg.IE_CE_UNKNOWN[0]:
                break

        if name == msg.IE_CE_UNKNOWN[0]:
            print(debug + name)

        gi = ""
        if gender == msg.M: gi = "M"
        if gender == msg.F: gi = "F"
        if gender == msg.N: gi = "N"

        text_elements.append(msg.N_ART[gi])

        # start with the length / cut
        arms, legs = self._getClothingLength()
        if arms:
            arms += gender
        if legs:
            if arms: arms += ", "
            legs += gender
        if arms+legs:
            text_elements.append(arms+legs)

        # append armor
        armor = self._getClothingArmor()
        if armor:
            armor += gender
            text_elements.append(armor)

        # check for the color
        color = self.item_data.get("color")
        if color:
            color = color.get().lower()
            if len(color) > 0:
                if color[-1] in ["a", "e"]:
                    color += msg.COLOR
                color += msg.IE_CE_LJOIN + gender
                text_elements.append(color)

        hoodies = [
            msg.IE_CE_SWEATER[0],
            msg.IE_CE_JACKET[0],
            msg.IE_CE_COAT[0],
            msg.IE_CE_OVERALL[0],
            msg.IE_CE_SHIRT[0],
            msg.IE_CE_DRESS[0]
        ]
        if name in hoodies and key[0] in ["1", "2", "F", "X"]:
            name = msg.IE_CE_HOOD[0] + name.lower()

        display_name = name

        # set the material
        material = self.item_data.get("material")
        if material:
            material = material.get()
            for ending in msg.IE_CE_DELE:
                if material.endswith(ending):
                    material = material[:-1]
            for ending in msg.IE_CE_ADDN:
                if material.endswith(ending):
                    material += "n"
            if len(material) > 0:
                if msg.IE_CE_NAMESPLIT in display_name:
                    s = name.split()
                    display_name = s[0] + " " + material + s[1].lower()
                elif "-" in name:
                    s = name.split("-")
                    display_name = material + s[-1].lower()
                else:
                    display_name = material+name.lower()

        text_elements.append(display_name)

        # adding pockets ...
        pockets = self._getClothingPockets()
        if pockets:
            text_elements.append(pockets)

        text_elements.append(".")

        addons = self._getClothingAddOns(name, gender)
        if len(addons) > 0:
            text_elements.append(addons)

        closure = self._getClothingClosure()
        if closure:
            text_elements.append(closure)

        quality = self._getClothingQuality()
        if quality:
            text_elements.append(quality)

        text = " ".join(text_elements)
        text = text.replace(" .", ".")
        self.description.delete("0.0", tk.END)
        self.description.insert(tk.END, text)

        if msg.IE_CE_NAMESPLIT in display_name:
            display_name = display_name.split()
            display_name = display_name[-1]
        self.item_data["name"].set(display_name)

    def _getClothingArmor(self):
        armor1, armor2 = self._getArmor()
        if armor2:
            return msg.IE_CE_ARMOR2
        if armor1:
            return msg.IE_CE_ARMOR1
        return ""

    def _getClothingAddOns(self, name, gender):
        gi = ""
        if gender == msg.M: gi = "M"
        if gender == msg.F: gi = "F"
        if gender == msg.N: gi = "N"

        text = ""

        selection = self._getSelectedOptions()
        trimmings = 0
        complex = 0
        fabric = 0

        for part in selection:
            options = selection[part]
            complex += options.get(msg.IE_CE_COMPLEX)
            trimmings += options.get(msg.IE_CE_TRIMMINGS)
            fabric += options.get(msg.IE_CE_CANVAS)

        # basic cut and leg length ...
        core = [msg.IE_CE_TORSO, msg.IE_CE_HIPS]
        legs = [msg.IE_CE_UPPERLEGS, msg.IE_CE_LOWERLEGS]
        core_fabric = 0
        leg_fabric = 0
        for el in core+legs:
            if el in selection.keys():
                if el in core:
                    core_fabric += selection.get(el).get(msg.IE_CE_CANVAS)
                else:
                    leg_fabric += selection.get(el).get(msg.IE_CE_CANVAS)

        leg_count = len(set(legs).intersection(selection.keys()))
        core_count = len(set(core).intersection(selection.keys()))
        leg_div = leg_count or 1
        core_div = core_count or 1
        leg_factor = int(2 * leg_fabric / leg_div)
        core_factor = int(2 * core_fabric / core_div)
        body = ""
        if core_count:
            cut = [
                msg.IE_CE_CONFORMING,
                msg.IE_CE_COMFY,
                msg.IE_CE_WIDE,
            ]
            body = cut[core_factor] + " " + msg.IE_CE_CUTLY

        # getting info about trimmings
        trimmings_factor = trimmings / len(selection)
        trimmings = ""
        if trimmings_factor > 0.5:
            if len(selection) > 3 and trimmings_factor > 0.75:
                trimmings = msg.IE_CE_RICH
            trimmings += msg.IE_CE_TRIMMED + msg.IE_CE_LJOIN + ", "
        body = trimmings + body

        # adding info concerning the legs
        if leg_count:
            dresses = [msg.IE_CE_DRESS[0], msg.IE_CE_SKIRT[0]]
            trousers = [msg.IE_CE_PANTS[0], msg.IE_CE_OVERALL[0]]
            coat = msg.IE_CE_COAT[0]
            cut = ["", "", ""]
            if name in coat:
                cut = [
                    msg.IE_CE_COAT_LEG_0,
                    msg.IE_CE_COAT_LEG_1,
                    msg.IE_CE_COAT_LEG_2,
                ]
            elif name in dresses:
                cut = [
                    msg.IE_CE_DRESS_LEG_0,
                    msg.IE_CE_DRESS_LEG_1,
                    msg.IE_CE_DRESS_LEG_2,
                ]
            elif name in trousers:
                cut = [
                    msg.IE_CE_PANTS_LEG_0,
                    msg.IE_CE_PANTS_LEG_1,
                    msg.IE_CE_PANTS_LEG_2,
                ]
            leg = cut[leg_factor]
            if len(leg) > 0:
                if len(body) > 0:
                    body = body+", "+leg

        # get information about the arms
        arms = {msg.IE_CE_UPPERARMS, msg.IE_CE_FOREARMS}
        index = ""
        for el in arms:
            if el in selection.keys():
                index += str(selection.get(el).get(msg.IE_CE_CANVAS) + 1)
            else:
                index += "0"
        arm_cut = msg.IE_CE_SLEEVE_DICT.get(index, "")

        # dealing with the intricacy of the cut
        complexity = ""
        if arm_cut:
            complexity = "und "
        complexity += msg.N_ART_ACC + " "
        complex_factor = complex / len(selection)
        if complex_factor < 0.5:
            if len(selection) > 3 and complex_factor < 0.25:
                complexity += msg.IE_CE_VERY + " "
            complexity += msg.IE_CE_PRIMITIVE + " "
        elif complex_factor >= 0.5:
            if len(selection) > 3 and complex_factor > 0.75:
                complexity += msg.IE_CE_VERY + " "
            complexity += msg.IE_CE_INTRICATE + " "
        complexity += msg.IE_CE_CUT

        description = msg.IE_CE_ADD_DESC1.format(
            art=msg.G_ART.get(gi)+" ",
            cut=body+" ",
            name=name+" ",
            has=random.choice(msg.IE_CE_HAS) + " ",
            arms=arm_cut+" ",
            style=complexity+"."
        )

        return description.replace("  ", " ")

    def _getClothingQuality(self):
        specials = 0
        for i in self._selectionIterator(msg.IE_CE_COMPLEX):
            specials += i * 1.5
        for i in self._selectionIterator(msg.IE_CE_CLOSURE):
            specials += i * 0.75
        for i in self._selectionIterator(msg.IE_CE_FABRIC):
            specials += i * 1.5
        for c, i in enumerate(self._selectionIterator(msg.IE_CE_TRIMMINGS),1):
            specials += i * 2.0

        layers_val = self.item_data[msg.IE_CE_SINGLE_LAYER]
        fabric_val = self.item_data[msg.IE_CE_FABRIC]

        assumed_qual = int((layers_val + fabric_val) * specials / c)
        if assumed_qual > 9: assumed_qual = 9
        quality_val = self.item_data[msg.IE_QUALITY]
        if assumed_qual > quality_val:
            cur_qual = msg.IE_CE_USED_QUAL[quality_val]
            orig_qual = msg.IE_CE_NEW_QUAL[assumed_qual] + " " + msg.IE_QUALITY
            quality = msg.IE_CE_USED.format(
                part=random.choice(msg.IE_CE_PART),
                state=cur_qual,
                quality=orig_qual
            )
        else:
            qual = msg.IE_CE_NEW_QUAL.get(quality_val) + " " + msg.IE_QUALITY
            quality = msg.IE_CE_NEW.format(
                part=random.choice(msg.IE_CE_PART),
                quality=qual
            )

        return quality

    def _getClothingPockets(self):
        pockets = 0
        for pocket in self._selectionIterator(msg.IE_CE_POCKETS):
            pockets += int(pocket)

        if pockets >= 3:
            if pockets >= 6:
                pockets = 4
            else:
                pockets = 3

        pocket_list = [
            msg.IE_CE_POCKETS_0,
            msg.IE_CE_POCKETS_1,
            msg.IE_CE_POCKETS_2,
            msg.IE_CE_POCKETS_3,
            msg.IE_CE_POCKETS_4
        ]

        key = self._getClothingKey()
        if key[2] == "0" and key[6] == "0":
            pockets = 0
        return pocket_list[pockets]

    def _getClothingLength(self):
        """ create descriptive strings for arm and leg length """

        key = self._getClothingKey()
        arms = ""
        legs = ""
        # arm length
        if key[2] != "0":
            if key[3] != "0":
                arms = msg.IE_CE_SHORT
            if key[4] != "0":
                arms = msg.IE_CE_LONG
            if arms:
                arms += msg.IE_CE_ARMLY
        # glove length
        elif key[5] != "0":
            if key[3] != "0":
                arms = msg.IE_CE_VERY + " "
            if key[4] != "0":
                arms += msg.IE_CE_LONG + msg.IE_CE_LJOIN

        # leg length
        if key[6] != "0":
            legs = msg.IE_CE_SHORT + msg.IE_CE_LJOIN
            if key[7] == "0":
                legs = msg.IE_CE_VERY + " " + legs
            if key[8] != "0":
                legs = msg.IE_CE_LONG + msg.IE_CE_LJOIN
            if key[9] != "0":
                legs = ""
        # socks / shoe length
        elif key[9] == "1":
            material_qualitity = self.item_data.get(msg.IE_CE_SINGLE_LAYER, 1)
            if material_qualitity == 1:
                variant = msg.IE_CE_LONG + msg.IE_CE_LJOIN
            else:
                variant = msg.IE_CE_HIGH
            if key[8] != "0":
                legs = variant
            if key[7] != "0":
                legs = msg.IE_CE_VERY + " " + legs

        return arms, legs

    def _getClothingClosure(self):
        value = self.item_data[msg.IE_CE_CLOSURE]
        closure = ""
        variants = {
            msg.IE_CE_BUTTONS: msg.IE_CE_BUTS,
            msg.IE_CE_ZIPPER: msg.IE_CE_ZIPS,
            msg.IE_CE_VELCRO: msg.IE_CE_VELCS,
            msg.IE_CE_LACING: msg.IE_CE_LACES,
            msg.IE_CE_BUCKLES: msg.IE_CE_BUCKS,
        }

        if value != msg.IE_CE_NO_CLOSURE:
            gendered = msg.IE_CE_CLOSURE_GENDERS[value]
            variant = random.choice(variants[value])
            closure = msg.IE_CE_CLOSURE_DESC.format(
                gendered=gendered,
                variant=variant,
                closure=value
            )

        return closure

    def _getClothingKey(self, lookup=0):
        """ Generate a description for the item based on the selections

        Args:
            lookup(int): rewrites the key for a fine graded lookup
                in the names dictionary - simplifies on pass 2 and 3

        Returns:
            string: selected bodyparts
        """
        selection = self._getSelectedOptions()
        body_parts = selection.keys()

        all_parts = [part[0] for part in self.body_parts]
        key = ""

        hips = msg.IE_CE_HIPS

        layers = self.item_data.get(msg.IE_CE_SINGLE_LAYER, 1)
        it = self._selectionIterator
        armor1 = sum([1 if i > 1 else 0 for i in it(msg.IE_CE_ARMOR1)])
        armor2 = sum([1 if i > 1 else 0 for i in it(msg.IE_CE_ARMOR2)])
        armor = armor1 + 2*armor2
        if armor > layers: layers = armor
        material = "1"
        if layers >= 2:
            material = "H"
        if layers >= 4:
            material = "A"

        for i, part in enumerate(all_parts):
            key_element = "0"

            if part in body_parts:
                key_element = "1"

                if lookup:
                    options = selection[part]
                    if options.get(msg.IE_CE_COMPLEX) > 0:
                        key_element = "2"
                    if options.get(msg.IE_CE_CANVAS) > 0:
                        key_element = "F"
                    if options.get(msg.IE_CE_CLOSURE) > 0:
                        if i in [1, 2, 6]:
                            key_element = "C"
                        else:
                            key_element = "2"
                    if part == hips and self.item_data["trousers"].get() == 1:
                        key_element = "T"

            key += key_element

        if key[1] == "C" and key[2] != "0":
            key = [i if c != 1 else "2" for c, i in enumerate(key)]
            key = "".join(key)

        if lookup >= 3:
            key = ["X" if i in ["1", "2", "F"] else i for i in key]
            key = "".join(key)

        if lookup >= 4:
            long = []
            if key[2] != "0" and key[0] == "X":
                long += [1, 1]
            else:
                long += [0, 0]
            if key[3] == "X":
                long += [0, 0, 1, 0]
            else:
                long += [0, 0, 0, 0]
            if key[7] == "X":
                long += [0, 0, 1, 0]
            else:
                long += [0, 0, 0, 0]
            key = ["X" if l else i for i, l in zip(key, long)]
            key = "".join(key)

        if lookup >= 5:
            if key[2] != "0" and key[0] == "X":
                long = [1, 1]
            else:
                long = [0, 0]
            if key[2] != "0":
                long += [0, 1, 1, 0]
            else:
                long += [0, 0, 0, 0]
            if key[6] != "0":
                long += [0, 1, 1, 0]
            else:
                long += [0, 0, 0, 0]
            key = ["X" if l else i for i, l in zip(key, long)]
            key = "".join(key)

        if lookup in [2, 4, 6]:
            key += "X"
        else:
            key += material

        return key

    def _generateClothingKey(self):
        """ generates a 'coverage key' """
        core = ["0 0", "1 0", "0 1", "1 1"]
        legs = ["000", "100", "110", "111", "011", "001"]
        arms = ["000", "100", "110", "011", "001"]
        head = ["00", "01", "10", "11"]

        core = random.choice(core)
        if core.startswith("1"):
            arms = arms[0:3]
        if core.endswith("1"):
            legs = legs[0:4]
        if core == "0 0":
            part = random.choice(["head", "legs", "arms"])
            if part == "head":
                head = head[2:4]
                legs = legs[0:1]
                arms = arms[0:1]
            elif part == "legs":
                head = head[0:1]
                legs = legs[3:6]
                arms = arms[0:1]
            elif part == "arms":
                head = head[0:1]
                legs = legs[0:1]
                arms = arms[3:5]
        if core == "0 1":
            head = head[0:1]
            arms = arms[0:1]
            legs = legs[0:3]
        if core == "1 0":
            head = head
            arms = arms[0:4]
            legs = legs[0:1]
        if core == "1 1":
            head = head[0:3]
            arms = arms[0:3]
            legs = legs[0:3]

        head = random.choice(head)
        arms = random.choice(arms)
        legs = random.choice(legs)
        core = core.split()

        key = head + core[0] + arms + core[1] + legs
        return key

    def _generateRandom(self):
        """ generating a random piece of clothing ..."""

        # clear out the data ...
        for part in self.body_parts:
            for element in self.elements:
                var_name = part[0] + "_" + element[0]
                value = 0
                if element[0] in [msg.IE_CE_ARMOR1, msg.IE_CE_ARMOR2]:
                    value = 1
                var = self.item_data[var_name]
                var.set(value)
        self.item_data["trousers"].set(0)

        # next we need a coverage key for a valid piece
        select = self._generateClothingKey()

        # are these trousers?
        if select[6] == "1":
            trousers = random.choice([0, 1])
            self.item_data["trousers"].set(trousers)
            if not trousers:
                if (select.endswith("1")
                    and select[6] == "0"
                    and select[7] == "1"
                ):
                    select = "0000000" + select[7:]

        # selecting the fabric and quality for the whole piece ...
        # removing unfitting materials for gloves, shoes and socks first ...
        unused = []
        if select[5] != "0":
            unused = msg.IE_CE_NOT_GLOVES
        feet = False
        if select[9] != "0":
            if select[6] == "0":
                feet = random.choice(["shoes", "socks"])
            else:
                feet = "socks"
            if feet == "shoes":
                unused = msg.IE_CE_NOT_SHOES
            else:
                unused = msg.IE_CE_NOT_SOCKS
        fabrics = msg.IE_CE_FABRICS
        fabrics = [f for f in fabrics if f not in unused]

        cheap = [fabric for fabric in fabrics if fabric[3] == 0]
        normal = [fabric for fabric in fabrics if fabric[3] == 1]
        expensive = [fabric for fabric in fabrics if fabric[3] == 2]

        price_ranges = {
            0.25: cheap,
            0.75: normal,
            1.0: expensive
        }
        rnd = random.random()
        for i, p_range in enumerate(price_ranges):
            if rnd <= p_range:
                fabrics = price_ranges[p_range]
                break

        fabric_qualities = [
            msg.IE_CE_SIMPLE,
            msg.IE_CE_ELEGANT,
            msg.IE_CE_RARE,
        ]
        self.item_data["F"].set(fabric_qualities[i])

        fabric, l_min, l_max, p = random.choice(fabrics)
        if feet == "shoes":
            l_min = 1
        if feet == "socks":
            l_min = 0
            l_may = 0
        layers = [
            msg.IE_CE_SINGLE_LAYER,
            msg.IE_CE_MULTI_LAYER,
            msg.IE_CE_MULTI_HEAVY
        ]
        self.item_data["material"].set(fabric)
        self.item_data["L"].set(random.choice(layers[l_min:l_max+1]))

        qualities = {
            0.1: msg.IE_QUALITY_3,
            0.25: msg.IE_QUALITY_4,
            0.33: msg.IE_QUALITY_5,
            0.66: msg.IE_QUALITY_6,
            0.75: msg.IE_QUALITY_7,
            0.9: msg.IE_QUALITY_8,
            1: msg.IE_QUALITY_9,
        }
        rnd = random.random()
        for qual in qualities:
            if rnd < qual:
                self.item_data["Q"].set(qualities[qual])
                break

        # chose a color
        self._generateRandomColor()

        # randomize per body part options
        closure_count = 0
        for i, value in enumerate(select):
            if value != "0":
                # basic selection
                body_part = self.body_parts[i]
                selected = self.elements[0]
                var_name = body_part[0] + "_" + selected[0]
                var = self.item_data[var_name]
                var.set(body_part[1])

                # armor
                armor1_name = body_part[0] + "_" + msg.IE_CE_ARMOR1
                armor2_name = body_part[0] + "_" + msg.IE_CE_ARMOR2
                armor1 = self.item_data[armor1_name]
                armor2 = self.item_data[armor2_name]
                if value == "A":
                    armor1.set(10)
                    armor2.set(10)
                else:
                    a1 = random.random()
                    if a1 <= 0.15:
                        armor1.set(10)
                        a2 = random.random()
                        if a2 <= 0.65:
                            armor2.set(10)
                        else:
                            armor2.set(1)
                    else:
                        armor1.set(1)
                        armor2.set(1)

                # closure
                closure_name = body_part[0] + "_" + msg.IE_CE_CLOSURE
                closure = self.item_data[closure_name]
                has_closure = {
                    msg.IE_CE_NECK: .9,
                    msg.IE_CE_TORSO: .5,
                    msg.IE_CE_UPPERARMS: .2,
                    msg.IE_CE_FOREARMS: .5,
                    msg.IE_CE_HIPS: .5,
                    msg.IE_CE_UPPERLEGS: .1,
                    msg.IE_CE_LOWERLEGS: .5,
                    msg.IE_CE_FEET: .5
                }
                if value == "C":
                    closure.set(1)
                    closure_count += 1
                else:
                    rnd = random.random()
                    if rnd <= has_closure.get(body_part[0], 0):
                        closure.set(1)
                        closure_count += 1
                    else:
                        closure.set(0)

                # complex cut
                complex_name = body_part[0] + "_" + msg.IE_CE_COMPLEX
                complex = self.item_data[complex_name]
                has_complex = {
                    msg.IE_CE_HEAD: .1,
                    msg.IE_CE_NECK: .5,
                    msg.IE_CE_TORSO: .5,
                    msg.IE_CE_UPPERARMS: .25,
                    msg.IE_CE_FOREARMS: .25,
                    msg.IE_CE_HANDS: .25,
                    msg.IE_CE_HIPS: .5,
                    msg.IE_CE_UPPERLEGS: .25,
                    msg.IE_CE_LOWERLEGS: .5,
                    msg.IE_CE_FEET: .25
                }
                if value == "2":
                    complex.set(1)
                else:
                    rnd = random.random()
                    if rnd <= has_complex.get(body_part[0], 0):
                        complex.set(1)
                    else:
                        complex.set(0)

                # lots of fabric
                fabric_name = body_part[0] + "_" + msg.IE_CE_CANVAS
                fabric = self.item_data[fabric_name]
                has_fabric = {
                    msg.IE_CE_HEAD: .1,
                    msg.IE_CE_NECK: .1,
                    msg.IE_CE_TORSO: .33,
                    msg.IE_CE_UPPERARMS: .33,
                    msg.IE_CE_FOREARMS: .33,
                    msg.IE_CE_HANDS: .1,
                    msg.IE_CE_HIPS: .33,
                    msg.IE_CE_UPPERLEGS: .33,
                    msg.IE_CE_LOWERLEGS: .5,
                    msg.IE_CE_FEET: .1
                }
                if value == "F":
                    fabric.set(1)
                else:
                    rnd = random.random()
                    if rnd <= has_fabric.get(body_part[0], 0):
                        fabric.set(1)
                    else:
                        fabric.set(0)

                # trimmings
                trimmings_name = body_part[0] + "_" + msg.IE_CE_TRIMMINGS
                trimmings = self.item_data[trimmings_name]
                has_trimmings = {
                    msg.IE_CE_HEAD: .1,
                    msg.IE_CE_NECK: .25,
                    msg.IE_CE_TORSO: .25,
                    msg.IE_CE_UPPERARMS: .1,
                    msg.IE_CE_FOREARMS: .25,
                    msg.IE_CE_HANDS: .25,
                    msg.IE_CE_HIPS: .25,
                    msg.IE_CE_UPPERLEGS: .25,
                    msg.IE_CE_LOWERLEGS: .25,
                    msg.IE_CE_FEET: .25
                }
                rnd = random.random()
                if rnd <= has_trimmings.get(body_part[0], 0):
                    trimmings.set(1)
                else:
                    trimmings.set(0)

                # pockets
                pockets_name = body_part[0] + "_" + msg.IE_CE_POCKETS
                pockets = self.item_data[pockets_name]
                has_pockets = {
                    msg.IE_CE_HEAD: [0, 0, 0, 0, 0, 0, 1],
                    msg.IE_CE_NECK: [0, 0, 0, 0, 0, 0, 1],
                    msg.IE_CE_TORSO: [0, 0, 0, 0, 1, 1, 2, 4],
                    msg.IE_CE_UPPERARMS: [0, 0, 0, 0, 2],
                    msg.IE_CE_FOREARMS: [0, 0, 0, 0, 2],
                    msg.IE_CE_HANDS: [0],
                    msg.IE_CE_HIPS: [0, 0, 0, 0, 1, 2, 2, 4],
                    msg.IE_CE_UPPERLEGS: [0, 0, 0, 0, 0, 1, 2, 2],
                    msg.IE_CE_LOWERLEGS: [0],
                    msg.IE_CE_FEET: [0]
                }
                pockets.set(random.choice(has_pockets[body_part[0]]))

        if closure_count:
            closures = [
                msg.IE_CE_BUCKLES,
                msg.IE_CE_BUTTONS,
                msg.IE_CE_VELCRO,
                msg.IE_CE_ZIPPER,
                msg.IE_CE_LACING
            ]
            self.item_data["C"].set(random.choice(closures))
        else:
            self.item_data["C"].set(msg.IE_CE_NO_CLOSURE)

        # finally write a description
        self._autoDescription()

    def _generateRandomColor(self):
        """ Generating a pseudo-random color """

        def modify(color):
            modificators = [""]
            if color not in msg.NOT_DARK:
                modificators.append(msg.DARK)
            if color not in msg.NOT_LIGHT:
                modificators.append(msg.LIGHT)
            if color not in msg.NOT_NEON:
                modificators.append(msg.NEON)
            modificators += (len(modificators)//2) * [""]
            return random.choice(modificators) + color

        base_color = random.choice(msg.ALL_COLORS)
        pattern_select = [msg.PLAIN, msg.PLAIN, msg.PLAIN, msg.PATTERNS, [""]]
        pattern = random.choice(pattern_select)
        if pattern == msg.PLAIN:
            color = modify(base_color)
            if color == base_color or color.startswith(msg.DARK):
                color += random.choice(["", "", " "+msg.SHIMMERING])
        else:
            pattern = random.choice(pattern)
            second_color = random.choice(msg.COLOR_COMBO.get(base_color))
            color = (modify(base_color)
                     + msg.COLOR_JOIN
                     + modify(second_color))
            if not pattern:
                if msg.NEON not in color and msg.LIGHT not in color:
                    color += msg.SHIMMERING
            else:
                color += " " + pattern

        color = color.strip()

        self.item_data["color"].set(color)

    def _createItem(self):
        """ create the item """

        # TODO: implement quantity
        item = et.Element("item")
        name = self.item_data["name"].get()
        price = self.item_data[msg.IE_PRICE]
        quality = self.item_data[msg.IE_QUALITY]
        weight = self._calculateWeight()
        item.set("name", name)
        item.set("price", str(price))
        item.set("weight", str(weight))
        item.set("quality", str(quality))
        item.set("quantity", "1")
        item.set("type", it.CLOTHING)

        armor = None
        armor1, armor2 = self._getArmor()
        if armor1 > 0:
            armor = "0/1"
        if armor2 > 0:
            armor = "0/2"
        if armor:
            item.set("type", it.ARMOR)
            et.SubElement(item, "damage", {"value": armor})

        color = self.item_data["color"].get()
        if color:
            et.SubElement(
                item,
                "option",
                {"name": msg.IE_CE_FABRIC_COLOR, "value": color}
            )

        material = self.item_data["material"].get()
        if material:
            et.SubElement(
                item,
                "option",
                {"name": msg.IE_CE_FABRIC_NAME, "value": material}
            )

        pockets = [int(i) for i in self._selectionIterator(msg.IE_CE_POCKETS)]
        if sum(pockets):
            et.SubElement(
                item,
                "container",
                {"name": name}
            )

        description = self.description.get("0.0", tk.END)
        if description:
            desc_tag = et.SubElement(item, "description")
            desc_tag.text = description

        self.char.addItem(item)
        self.main.updateItemList()
