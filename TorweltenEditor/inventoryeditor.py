import tkinter as tk
import xml.etree.ElementTree as et
import config
from tooltip import ToolTip

msg = config.Messages()
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

        self.items = None
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
        self.content_frame = tk.Frame(self)
        
        self.group_frame = tk.Frame(self.content_frame)
        self.group_frame.pack(side=tk.LEFT, fill=tk.Y, expand=1)
        
        self.right_frame = tk.Frame(self.content_frame)
        self.main_display = tk.Frame(self.right_frame)
        
        self.selector_list_frame = tk.Frame(self.main_display)
        self.selector_list = tk.Listbox(self.selector_list_frame, width=30)
        self.selector_list.bind("<<ListboxSelect>>", self.selectionChanged)
        self.selector_scroll = tk.Scrollbar(
            self.selector_list_frame,
            orient=tk.VERTICAL,
            command=self.selector_list.yview
        )
        self.selector_list.config(yscrollcommand=self.selector_scroll.set)
        self.selector_scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=1)
        self.selector_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.selector_list_frame.pack(
            side=tk.LEFT,
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
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        
        self.content_frame.pack(fill=tk.BOTH, expand=1)

        # reserved for sub_modules ...
        self.sub_module = tk.Frame(self.main_display)

        self.displayGroups()

    def displayGroups(self):
        # clear the current buttons
        current_group_buttons = self.group_frame.winfo_children()
        for widget in current_group_buttons:
            widget.destroy()

        #  clear the itemlist
        self.selector_list.delete(0, tk.END)

        groups = self.itemlist.getGroups()
        for group in groups:
            name = group.get("name")
            button = tk.Button(self.group_frame, text=name, width=25)
            button.bind("<Button-1>", self.displaySubgroups)
            button.pack()
        button = tk.Button(self.group_frame, text=msg.IE_CUSTOM_ITEM, width=25)
        button.bind("<Button-1>", self.customItem)
        button.pack()
    
    def displaySubgroups(self, event):
        if not self.item_frame.winfo_ismapped():
            self.displayItemFrame()

        clicked_button = event.widget
        group_name = clicked_button.cget("text")
        group = self.itemlist.getGroup(group_name)

        # clear the current buttons
        current_group_buttons = self.group_frame.winfo_children()
        for widget in current_group_buttons:
            widget.destroy()

        back_button = tk.Button(
            self.group_frame,
            text=msg.IE_BACK,
            width=25,
            command=self.displayGroups
        )
        back_button.pack()
        for subgroup in group:
            button = tk.Button(
                self.group_frame,
                text=subgroup.get("name"),
                width=25
            )
            button.bind("<Button-1>", self.displayItems)
            button.pack()

    def displayItems(self, event):
        clicked = event.widget

        buttons = self.group_frame.winfo_children()
        for button in buttons:
            button.config(background="#eeeeee")

        clicked.config(background="#666666")

        # clear the list ...
        self.selector_list.delete(0, tk.END)

        # fill the list
        subgroup_name = clicked.cget("text")
        self.items = self.itemlist.getItems(subgroup_name)

        for item in self.items:
            self.selector_list.insert(tk.END, item.get("name"))
        self.selector_list.focus()

    def selectionChanged(self, event=None):
        """ Checks if the selected item needs to be changed

        Args:
            event (unused): passed from the .bind()
        """

        if self.selector_list.focus_get() == self.selector_list:
            self.displayItem()

    def displayItem(self):

        # clear the add item frame
        widgets = self.item_add_frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        self.item_desc_edited = False
        selection_id = self.selector_list.curselection()

        if not selection_id:
            return

        selected_name = self.selector_list.get(selection_id)
        self.cur_selection = selection_id
        
        for item in self.items:
            if item.get("name") == selected_name:
                break

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
        self.item_frame.pack_forget()

        # clear the sub_module frame
        widgets = self.sub_module.winfo_children()
        for widget in widgets:
            widget.destroy()

        self.item_data.clear()
        self.item_data_trace.clear()

        # building the screen an setting up variables to hold the 
        # given data ... 
        name_var = tk.StringVar()
        self.item_data["name"] = name_var
        top_frame = tk.Frame(self.sub_module)
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

        damage_frame = tk.LabelFrame(self.sub_module, text=msg.IE_DAMAGE_HEADER)
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

        caliber_frame = tk.LabelFrame(self.sub_module, text=msg.IE_CALIBER_HEAD)
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
            self.sub_module,
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
        description_frame = tk.LabelFrame(self.sub_module, text=text)
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
            self.sub_module,
            type_var,
            *itemtypes
        ).pack(fill=tk.X)

        tk.Button(
            self.sub_module,
            text=msg.IE_ADD_ITEM,
            command=self._addCustomItem
        ).pack(fill=tk.X)

        self.sub_module.pack(side=tk.RIGHT)

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

                    if not -9 <= s <= 9 or not-7 <= d <= 7:
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

