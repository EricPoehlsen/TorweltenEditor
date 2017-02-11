import tkinter as tk
import xml.etree.ElementTree as et
import config

msg = config.Messages()
it = config.ItemTypes()

#this class creates the InventoryEditor        
class InventoryEditor:
    def __init__(self,main):
        # get the data from the application
        self.char = main.char
        self.itemlist = main.itemlist
        self.main = main

        self.cur_selection = 0
        
        # prepare variables for the item
        self.item = 0
        self.new_item = 0
        self.item_data = {}
        self.item_data_trace = {}
        self.item_desc_edited = False

        # costruct the window
        self.inv_editor = tk.Toplevel()
        self.inv_editor.protocol("WM_DELETE_WINDOW", self.close)
        self.inv_editor.title(msg.IE_TITLE)
        self.content_frame = tk.Frame(self.inv_editor)
        
        self.group_frame = tk.Frame(self.content_frame)
        self.group_frame.pack(side = tk.LEFT, fill = tk.Y, expand = 1)
        
        self.right_frame = tk.Frame(self.content_frame)
        self.main_display = tk.Frame(self.right_frame)
        
        self.selector_list_frame = tk.Frame(self.main_display)
        self.selector_list = tk.Listbox(self.selector_list_frame, width = 30)
        self.selector_list.bind("<<ListboxSelect>>", self.selectionChanged)
        self.selector_scroll = tk.Scrollbar(self.selector_list_frame,orient = tk.VERTICAL,command = self.selector_list.yview)
        self.selector_list.config(yscrollcommand = self.selector_scroll.set)
        self.selector_scroll.pack(side = tk.RIGHT, fill = tk.Y, expand = 1)
        self.selector_list.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        self.selector_list_frame.pack(side = tk.LEFT, fill = tk.Y, expand = 1, anchor = tk.W)
        self.selector_list.focus()

        self.item_frame = tk.Frame(self.main_display)
        self.item_title_frame = tk.Frame(self.item_frame)
        self.item_title = tk.Label(self.item_title_frame, font = "Arial 16 bold", text = msg.ITEMNAME, justify = tk.LEFT)
        self.item_title.pack(side = tk.LEFT, fill = tk.X, anchor = tk.W)
        self.item_avail = tk.Label(self.item_title_frame, font = "Arial 16 bold", text = msg.IE_AVAIL)
        self.item_avail.pack(side = tk.RIGHT, anchor = tk.E)
        self.item_price = tk.Label(self.item_title_frame,font = "Arial 16 bold",text = msg.IE_COST)
        self.item_price.pack(side = tk.RIGHT, anchor = tk.E)
        self.item_title_frame.pack(side = tk.TOP, anchor = tk.NW, fill = tk.X)
        self.item_info_text = tk.Text(self.item_frame, width = 70, height = 12, wrap = tk.WORD)
        self.item_info_text.bind("<BackSpace>", self.descriptionEdited)
        self.item_info_text.bind("<Delete>",self.descriptionEdited)
        self.item_info_text.pack()
        self.item_add_frame = tk.Frame(self.item_frame)
        
        self.item_add_frame.pack()
        self.item_frame.pack(side = tk.LEFT)

        self.main_display.pack(fill = tk.BOTH, expand = 1, anchor = tk.W)
        self.right_frame.pack(side = tk.RIGHT, fill = tk.BOTH, expand = 1)
        
        self.content_frame.pack(fill = tk.BOTH, expand = 1)

        self.displayGroups()

    def displayGroups(self):
        # clear the current buttons
        current_group_buttons = self.group_frame.winfo_children()
        for widget in current_group_buttons:
            widget.destroy()

        #  clear the itemlist
        self.selector_list.delete(0,tk.END)

        groups = self.itemlist.getGroups()
        for group in groups:
            name = group.get("name")
            button = tk.Button(self.group_frame, text = name, width = 25)
            button.bind("<Button-1>", self.displaySubgroups)
            button.pack()
    
    def displaySubgroups(self,event):
        clicked_button = event.widget
        group_name = clicked_button.cget("text")
        group = self.itemlist.getGroup(group_name)

        # clear the current buttons
        current_group_buttons = self.group_frame.winfo_children()
        for widget in current_group_buttons:
            widget.destroy()

        back_button = tk.Button(self.group_frame, text = msg.IE_BACK, width = 25, command = self.displayGroups)
        back_button.pack()
        for subgroup in group:
            button = tk.Button(self.group_frame, text = subgroup.get("name"), width = 25)
            button.bind("<Button-1>", self.displayItems)
            button.pack()

    def displayItems(self,event):
        clicked = event.widget

        buttons = self.group_frame.winfo_children()
        for button in buttons:
            button.config(background = "#eeeeee")

        clicked.config(background = "#666666")

        # clear the list ...
        self.selector_list.delete(0,tk.END)

        # fill the list
        subgroup_name = clicked.cget("text")

        self.items = self.itemlist.getItems(subgroup_name)

        for item in self.items:
            self.selector_list.insert(tk.END,item.get("name"))

    def selectionChanged(self, event=None):

        print(self.selector_list.focus_get())

        if self.selector_list.focus_get() == self.selector_list:
            self.displayItem(event)

    def displayItem(self,event = None):

        # clear the add item frame
        widgets = self.item_add_frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        self.item_desc_edited = False
        selection_id = self.selector_list.curselection()
        selected_name = self.selector_list.get(selection_id)
        self.cur_selection = selection_id
        
        for item in self.items:
            if item.get("name") == selected_name:
                break
        
        # create the new item (as we do not want to change our item list)
        new_item = et.Element("item")
        new_item.set("name", selected_name)
        new_item.set("weight", item.get("weight","0"))
        new_item.set("type", item.get("type",it.GENERIC))
        self.item = item
        self.new_item = new_item
        
        # transfer basic tags ...
        damage = self.item.find("damage") 
        if damage is not None: new_item.append(damage)
        container = self.item.find("container")
        if container is not None: new_item.append(container)
        ammo = self.item.find("ammo")
        if ammo is not None: new_item.append(ammo)
        
        # set initial price        
        price = float(item.get("price"))
        self.setPrice(price)

        # update the info ...
        self.item_title.config(text = selected_name)
        description = item.find("description")

        # add the text    
        if description is not None:
            self.setDescription(description)
        else: 
            self.item_info_text.delete("1.0",tk.END)
            
        # add selectors for quantity, quality and other options stuff ... 
        options = item.findall("option")
        for option in options:
            option_name = option.get("name")
            self.item_data[option_name] = tk.StringVar()
            self.item_data[option_name].trace("w", self.variable_changed)
            self.item_data_trace[str(self.item_data[option_name])] = option_name

            # are there values???
            option_values = option.get("values")
            
            option_text = tk.Label(self.item_add_frame,text = option_name)
            option_text.pack(side = tk.LEFT)

            option_widget = tk.Entry(self.item_add_frame, width = 15, textvariable = self.item_data[option_name])
            if option_values:
                option_values = option_values.split(",")
                self.item_data[option_name].set(option_values[0])
                option_widget = tk.OptionMenu(self.item_add_frame, self.item_data[option_name], *option_values)

            option_widget.pack(side = tk.LEFT)

        # add quantity scroller
        self.item_data["quantity"] = tk.StringVar()
        self.item_data["quantity"].trace("w", self.variable_changed)
        self.item_data_trace[str(self.item_data["quantity"])] = "quantity"

        self.item_data["quantity"].set(1)
        quantity_text = tk.Label(self.item_add_frame, text = msg.IE_QUANTITY)
        quantity_text.pack(side=tk.LEFT)
        quantity_scroller = tk.Spinbox(self.item_add_frame, textvariable = self.item_data["quantity"], width = 3)
        
        # is there a standard quantity info on the item?
        packs = item.findall("./pack")
        packs_values = []
        widget_width = 0
        for pack in packs:
            pack_name = pack.get("name")
            packs_values.append(pack_name)
            if len(pack_name) > widget_width: widget_width = len(pack_name)
        
        if len(packs_values) > 0:
            quantity_scroller.config(values = packs_values, width = widget_width)
        else: quantity_scroller.config(from_ = 1, to = 100)

        quantity_scroller.pack(side=tk.LEFT)
        
        # #adding a quality scroller 

        # check for minimum and maximum quality
        min_qual = self.getMinQuality()
        max_qual = self.getMaxQuality()
        base_qual = 6
        if base_qual < min_qual: base_qual = min_qual
        if base_qual > max_qual: base_qual = max_qual
        
        # create the variables
        self.item_data["quality"] = tk.StringVar()
        self.item_data["quality"].set(base_qual)
        self.item_data["quality"].trace("w", self.variable_changed)
        self.item_data_trace[str(self.item_data["quality"])] = "quality"
        
        # create an place the widgets
        quality_text = tk.Label(self.item_add_frame, text = msg.IE_QUALITY)
        quality_text.pack(side=tk.LEFT)
        quality_scroller = tk.Spinbox(self.item_add_frame, from_ = min_qual, to = max_qual, textvariable = self.item_data["quality"], width = 3)
        quality_scroller.pack(side = tk.LEFT)

        # set the starting quality
        self.new_item.set("quality",str(base_qual))

        # adding the button to add the item
        button = tk.Button(
            self.item_add_frame,
            text=msg.IE_BUY,
            command=self.addItem
        )
        button.pack(side = tk.LEFT)
        
    
    # Set a custom text for the item
    def setText(self):
        current_content = self.item_info_text.get("1.0",tk.END)
        description = et.Element("description")
        description.text = current_content
        self.new_item.append(description)
            
    # Displays the description of the item 
    def setDescription(self,description):
        """ Setting the description
        Updates self.item_info_text a tk.Text widget
        description: et.Element (intended to handle <description> displays content from <text> childnodes 
        return: INT - length of text
        """
        # clear the widget
        self.item_info_text.delete("1.0",tk.END)

        full_string = ""
        # add text that is without <text> tag ...
        if description.text is not None:
            old_index = self.item_info_text.index(tk.CURRENT)
            self.item_info_text.insert(tk.END,description.text)
            full_string = full_string + description.text
            new_index = self.item_info_text.index(tk.CURRENT)
            format_string = config.Style.FONT + " " + config.Style.SIZE
            self.item_info_text.tag_add("basic", old_index, new_index)
            self.item_info_text.tag_config("basic", font = format_string)

        # add text inside <text> tags
        text_fragments = description.findall("./text")
        fragment_count = 0
        for fragment in text_fragments:
            if fragment.text == None: fragment.text = " "
            full_string = full_string + fragment.text
            old_index = self.item_info_text.index(tk.CURRENT)
            self.item_info_text.insert(tk.END,fragment.text)
            new_index = self.item_info_text.index(tk.CURRENT)
            fragment_font = fragment.get("font")
            fragment_size = fragment.get("size")
            fragment_style = fragment.get("style")
            format_string = ""
            if (fragment_font is not None):
                format_string = fragment_font
            else: 
                format_string = config.Style.FONT

            if (fragment_size is not None):
                format_string = format_string + " " + fragment_size
            else:
                format_string = format_string + " " + config.Style.SIZE

            if (fragment_style is not None):
                format_string = format_string + " " + fragment_style

            fragment_id = "fragment" + str(fragment_count)
            self.item_info_text.tag_add(fragment_id, old_index, new_index)
            self.item_info_text.tag_config(fragment_id, font = format_string)
            fragment_count += 1
        return len(full_string)


    # set the price of the item to a new value
    def setPrice(self,value):
        """ updates the price of self.new_item (et.Element) and self.item_price (tk.Label)
        value: FLOAT [STRING (if valid . or , separated number) or INT will be transformed if]
        """
        
        text_value = msg.IE_PRICE + ": "
        float_value = 0.0

        if type(value) == str:
            if "." in value: value = value.split(".")
            elif "," in value: value = value.split(",")
            else: value = [value,"00"]
            
            # raise a value error if the string can't be transformed to a number!
            try: 
                test = int(value[1])
            except ValueError:
                raise ValueError("Input string needs to be a number: 0.00 or 0,00")
            else: 
                if test < 0: raise ValueError("Input string needs to be a number: 0.00 or 0,00")

            if len(value[1]) > 2: value[1] = value[1][:2]
            float_value = float(value[0] + "." + value[1])
            text_value = text_value + value[0] + "," + value[1]
        elif type(value) == int:
            float_value = float(value)
            text_value = text_value + str(value) + ",00"
        elif type(value) == float:
            value = round(value,2)
            float_value = value
            value = str(value).split(".")
            if len(value[1]) == 1: value[1] = value[1] + "0"
            elif len(value[1]) > 2: value[1] = value[1][:2]
            text_value = text_value + value[0] + "," + value[1]
        else: 
            input = type(value).__name__.upper()
            raise TypeError("Input was " + input + " needs to be FLOAT, INT or STR")

        self.item_price.config(text = text_value)
        self.new_item.set("price", str(float_value))


    # get the price of an item
    def getPrice(self):
        """
        retrieve the stored value from the Element self.new_item
        return: FLOAT
        """
        price = float(self.new_item.get("price","1"))
        return price


    # trace the variables        
    def variable_changed(self,tcl_var,empty,mode):
        """
        this method traces the variable changes of an item ...
        tcl_var: STRING tcl name of the passing variable
        empty: is an empty string
        mode: STRING: w or r
        """
        changed = self.item_data_trace[tcl_var]
        value = self.item_data[changed].get()

        if changed == "quantity": self.quantityChanged(value)
        elif changed == "quality": self.qualityChanged(value)
        else:
            # write the selected option into the new item
            element = self.new_item.find("option[@name='"+changed+"']")
            if element is None:
                element = et.Element("option")
                element.set("name",changed)
                self.new_item.append(element)
            
            element = self.new_item.find("option[@name='"+changed+"']")
            element.set("value",str(value))

            # now we have to find out if the selected option changes more
            # get the option of the item
            option = self.item.find("option[@name='"+changed+"']") 
            
            # find out if there is a tag which is modified
            tag_name = option.get("tag") 
            tag = None
            if tag_name: tag = self.item.find(tag_name+"[@name='"+value+"']")
            if tag is not None:
                old_tag = self.new_item.find("./"+tag_name)
                self.new_item.remove(old_tag)
                self.new_item.append(tag)

            # find out if this option modifies an attribute (price, weight, avail)
            # these are stores as space separeted tuples (price:20 weight:20 ...) 
            attrib = option.get("attrib")
            if attrib is not None:
                attrib_list = attrib.split()
                for attrib_tuple in attrib_list: 
                    elements = attrib_tuple.split(":")
                    name = elements[0]
                    value = elements[1]
                    self.item.set(name,value)
                    # make adjustments based on the quality
                    if name == "price" or name == "avail":
                        qualtity = self.item.get("quality","7")
                        self.qualityChanged(qualtity,direct = True)


                    
    # trace the variable for the item quantity    
    def quantityChanged(self,quantity):
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
        
        old_quantity = self.new_item.get("quantity","1")
        self.new_item.set("quantity", str(quantity))
        
        # update price
        old_price = self.getPrice() / int(old_quantity) 
        new_price = old_price * quantity
        self.setPrice(new_price)
    
    
    # the quality has been changed
    def qualityChanged(self,value,direct=False):
        """
        handling changes of the qualtity selector
        value: STRING (will be stripped to a INT range 3:9)
        """    
        # #cleaning the value!
        try:
            value = int(value)
        except ValueError:
            value = 6

        min = self.getMinQuality()
        max = self.getMaxQuality()
        if value > max: value = max
        if value < min: value = min
        
        # the quality matrix
        quality = {
            3:[0.1, 2,msg.IE_QUALITY_3],
            4:[0.25,1,msg.IE_QUALITY_4],
            5:[0.5,-1,msg.IE_QUALITY_5],
            6:[1.0, 0,msg.IE_QUALITY_6],
            7:[1.5, 1,msg.IE_QUALITY_7],
            8:[2.5, 3,msg.IE_QUALITY_8],
            9:[5.0, 4,msg.IE_QUALITY_9]
        }        
        
        old_quality = int(self.new_item.get("quality","6"))
        old_price = self.getPrice() / quality[old_quality][0]
        
        # don't adjust for former quality 
        if direct: 
            old_price = self.getPrice()

        new_price = old_price * quality[value][0]
        self.new_item.set("quality",str(value))
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
            if len(quality) == 2: max_quality = quality[1]
            else: max_quality = quality[0]

        return int(max_quality)

    # the user changed the description
    def descriptionEdited(self,event):
        self.item_desc_edited = True

    def addItem(self):
        self.setText()

        # add the item
        self.char.addItem(self.new_item)
        self.main.updateItemList()
        # show again, to make sure a new item is generated ...
        self.selector_list.selection_set(self.cur_selection)
        self.displayItem()

    def close(self):
        self.inv_editor.destroy()
        self.main.open_windows["inv"] = 0
