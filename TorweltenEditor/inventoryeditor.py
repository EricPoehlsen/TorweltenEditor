import tkinter as tk
from PIL import ImageTk
import xml.etree.ElementTree as et
import config
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
        back_button.pack(fill=tk.X)
        if group_name == msg.IE_CLOTHING_GROUP:
            editor_button = tk.Button(
                self.group_frame,
                text=msg.IE_CLOTHING_EDITOR,
                width=25,
                command=self.customClothing
            )
            editor_button.pack(fill=tk.X)

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

    def customClothing(self):
        """ Creating a new custom clothing item

        event (unused) called by a click event

        """

        # hiding the standard item frame
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
        self.description = None
        self.trousers = None

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

    def _topView(self,parent):
        name_var = tk.StringVar()
        self.item_data["name"] = name_var
        name_var.trace("w", self._calculateCost)
        frame = tk.Frame(parent)
        name_frame = tk.LabelFrame(frame, text=msg.IE_NAME)
        tk.Entry(
            name_frame,
            width=40,
            textvariable=name_var
        ).pack(fill=tk.X)
        name_frame.pack(side=tk.LEFT)
        # name_frame.bind("<Enter>", lambda e: self.showTooltip(e, "name"))
        return frame

    def _selectionView(self, parent):
        """ creates a frame with option selection for customClothing

        Args:
            parent (tk.Frame): frame to display it in

        Note:
            uses .grid() layout
        """

        frame = tk.LabelFrame(parent, text=msg.IE_CE_SELECTION)
        frame.columnconfigure(0, weight=20)

        self._selectionHeaders(frame)

        for row, part in enumerate(self.body_parts, start=1):
            label = tk.Label(frame, text=part[0])
            label.grid(row=row, column=0, sticky=tk.W)

            for col, el in enumerate(self.elements, start=1):
                if el[2] == -1:
                    el[2] = part[1]
                var = tk.IntVar()
                var.trace("w", self._calculateCost)
                legs = [msg.IE_CE_UPPERLEGS, msg.IE_CE_HIPS]
                if part[0] in legs and col == 1:
                    var.trace(
                        "w",
                        lambda n, e, v, var=var:
                            self._trousersToggle(var))
                if col == 2 or col == 3:
                    var.trace("w", self._armorToggle)
                self.item_data[part[0]+"_"+el[0]] = var
                self.item_data_trace[str(var)] = part[0]+"_"+el[0]
                var.set(el[1])
                cb = tk.Checkbutton(
                    frame,
                    var=var,
                    offvalue=el[1],
                    onvalue=el[2],
                )
                if col == 1:
                    cb.bind("<Button-1>", self._toggleCheckbuttons)
                if col > 1:
                    cb.config(state=tk.DISABLED)
                cb.grid(row=row, column=col)

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

    def _selectionHeaders(self, parent):
        images = [
            ImageTk.PhotoImage(file="images/ie_tick.png"),
            ImageTk.PhotoImage(file="images/ie_armor1.png"),
            ImageTk.PhotoImage(file="images/ie_armor2.png"),
            ImageTk.PhotoImage(file="images/ie_closure.png"),
            ImageTk.PhotoImage(file="images/ie_complex.png"),
            ImageTk.PhotoImage(file="images/ie_fabric.png"),
            ImageTk.PhotoImage(file="images/ie_trimmings.png"),
            ImageTk.PhotoImage(file="images/ie_pockets.png")
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
        var = tk.StringVar()
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
        l_var = tk.StringVar()
        l_var.trace("w", lambda n, e, m: self._layers(l_var))
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
        var = tk.StringVar()
        var.set(fabric_group[0])
        var.trace("w", lambda n, e, m: self._fabric(var))
        button = tk.OptionMenu(
            frame,
            var,
            *fabric_group
        )
        button.pack(fill=tk.X, expand=1)
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
        # TODO: Implement an autodescription
        self.item_data["description"] = tk.StringVar()
        frame = tk.LabelFrame(parent, text=msg.IE_DESCRIPTION)
        icon = ImageTk.PhotoImage(file="ui_img/text_signature.png"),

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
        print(selected)
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
            text = msg.IE_BUY + "\n" + str(price)
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
        parent_name = event.widget.winfo_parent()
        toplevel = event.widget.winfo_toplevel()
        parent = toplevel.nametowidget(parent_name)
        var_name = event.widget.cget("variable")
        var_trace = self.item_data_trace[str(var_name)]
        var = self.item_data[var_trace]

        widgets = parent.winfo_children()
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

        selection = self._getSelectedOptions()
        armor1 = 0
        armor2 = 0
        for key in selection:
            part_data = selection[key]
            for sub in part_data:
                if msg.IE_CE_ARMOR2 in sub:
                    armor2 += int(part_data[sub] / 10)
                elif msg.IE_CE_ARMOR1 in sub:
                    armor1 += int(part_data[sub] / 10)
        return armor1, armor2

    def _autoDescription(self):
        """ Generate a description for the item based on the selections """
        selection = self._getSelectedOptions()
        body_parts = selection.keys()
        layers = self.item_data[msg.IE_CE_SINGLE_LAYER]

        all_parts = [part[0] for part in self.body_parts]

        clothing_key = ""
        for part in all_parts:
            body_part = selection.get(part, "0")
            if body_part != "0":
                value = 1
                if (body_part.get(msg.IE_CE_COMPLEX, 0) == 1
                    and part in [msg.IE_CE_HEAD]
                ):
                    value = 2
                if body_part.get(msg.IE_CE_FABRIC, 0) == 1:
                    value = "F"
                if body_part.get(msg.IE_CE_CLOSURE, 0) == 1:
                    value = "C"
                if (self.item_data["trousers"].get() == 1
                    and part == msg.IE_CE_HIPS
                ):
                    value = "T"
                if (body_part.get(msg.IE_CE_ARMOR2, 0) == 10
                    and part == msg.IE_CE_HEAD
                ):
                    value = "H"

                body_part = str(value)
            clothing_key += body_part

        clothing_names = msg.IE_CLOTHING_NAMES

        self.description.delete("0.0",tk.END)
        name = clothing_names.get(clothing_key, "unknown")
        if name == "unknown":
            print(clothing_key)
        self.description.insert(tk.END, name)

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
            armor = "1/0"
        if armor2 > 0:
            armor = "2/0"
        if armor:
            item.set("type", it.ARMOR)
            et.SubElement(item, "damage", {"value": armor})

        description = self.description.get("0.0", tk.END)
        if description:
            desc_tag = et.SubElement(item, "description")
            desc_tag.text = description

        self.char.addItem(item)
        self.main.updateItemList()


        pass
