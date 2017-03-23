import tkinter as tk
import xml.etree.ElementTree as et
import config

page = config.Page()
msg = config.Messages()
it = config.ItemTypes()


class ModuleEditor(tk.Toplevel):
    """
    main: parent window
    location: string "col row"
    """

    def __init__(self, main, location):
        super().__init__()

        self.minsize(250, 1)

        self.main = main
        main.open_windows["mod_ed"] = self

        location = location.split()
        self.col = int(location[0])
        self.row = int(location[1])
        self.size = ""

        # store widgets for access
        self.widgets = {}
        self.vars = {}
        self.var_names = {}

        self.page = main.template.find("page[@num='"+str(main.active_page)+"']")
        self.module = None

        self.space = self._checkLocation()
        
        self.frame = tk.Frame(self)
        if self.module is None:
            self._newModule(self.frame)
        else:
            self._editModule(self.frame)
        self.frame.pack(fill=tk.BOTH, anchor=tk.N)

        self.protocol("WM_DELETE_WINDOW", self.close)

    def _checkLocation(self):
        self.module = self._getModule()
        space = (0, 0)
        if self.module is None:
            space = self._getSpace()
        return space
    
    # add a new module
    def _newModule(self, frame):
        tk.Label(frame, text=msg.ME_NEW).pack(fill=tk.X, expand=1)

        mod_types = (
            msg.PDF_ATTRIBUTES,
            msg.PDF_TRAITS,
            msg.PDF_SKILLS,
            msg.PDF_EQUIPMENT,
            msg.PDF_WEAPONS,
            msg.PDF_CONTACTS,
            msg.PDF_EWT,
            msg.PDF_IMAGE,
            msg.PDF_NOTES)
        # this will be the frame for the option selection ... 

        selected_type = tk.StringVar()
        
        selected_type.trace("w", self._modTypeChanged)
        self.vars[str(selected_type)] = selected_type
        self.var_names["module"] = str(selected_type)
        select_button = tk.OptionMenu(
            frame,
            selected_type,
            *mod_types)
        selected_type.set(mod_types[0])
        select_button.pack(fill=tk.X, expand=1)
        row = str(self.row)
        col = str(self.col)
        id = str(self.main.getHighestModuleId()+1)
        
        sub_frame = tk.Frame(frame)
        self.widgets["options"] = option_frame = tk.Frame(sub_frame)
        
        option_frame.pack(fill=tk.X)

        selected_type.set(mod_types[0])

        sub_frame.pack(fill=tk.BOTH, expand=1)
        add_button = tk.Button(frame, text=msg.ME_ADD, command=self._addModule)
        add_button.pack(fill=tk.X, anchor=tk.S)

    # edit or delete a module ...
    def _editModule(self, frame):
        tk.Label(frame, text=msg.ME_EDIT).pack()
        mod_type = self.module.get("type")

        # change size ... 
        self.space = self._getSpace()
        sizes = self._potentialSizes()

        if mod_type == page.MOD_ATTRIBUTES:
            if msg.PDF_DOUBLE in sizes:
                sizes = [msg.PDF_DOUBLE]
            else:
                sizes = [""]

        if mod_type == page.MOD_EWT:
            if msg.PDF_SINGLE in sizes:
                sizes = [msg.PDF_SINGLE]
            else:
                sizes = [""]
        
        tk.Label(frame, text=msg.ME_CHANGE_SIZE).pack()
        size = tk.StringVar()
        self.vars[str(size)] = size
        self.var_names["size"] = str(size)
        
        cur_size = self.module.get("size")

        size_names = {
            page.SINGLE: msg.PDF_SINGLE,
            page.WIDE: msg.PDF_WIDE,
            page.DOUBLE: msg.PDF_DOUBLE,
            page.QUART: msg.PDF_QUART,
            page.TRIPLE: msg.PDF_TRIPLE,
            page.BIG: msg.PDF_BIG,
            page.FULL: msg.PDF_FULL,
            page.HALF: msg.PDF_HALF
        }
        cur_size = size_names[cur_size]
        
        size_button = tk.OptionMenu(frame, size, *tuple(sizes))
        size.set(cur_size)
        size_button.pack(fill=tk.X)
        if mod_type in [
            page.MOD_TRAITS,
            page.MOD_WEAPONS,
            page.MOD_EQUIPMENT,
            page.MOD_CONTACTS
        ]:
            info_lines = tk.StringVar()
            self.vars[str(info_lines)] = info_lines
            self.var_names["info_lines"] = str(info_lines)
            info_lines_tag = self.module.find("param[@name='info_lines']")
            if info_lines_tag is not None:
                info_lines.set(info_lines_tag.get("value", "0"))
            else:
                info_lines.set("0")
            sub_frame = tk.Frame(frame)
            tk.Label(sub_frame, text=msg.ME_TEXTLINES).pack(side=tk.LEFT)
            tk.Spinbox(
                sub_frame,
                textvariable=info_lines,
                from_=0,
                to=5,
                width=2
            ).pack(side=tk.LEFT)
            sub_frame.pack()

        tk.Button(frame, text=msg.ME_SAVE, command=self._updateModule).pack()
        tk.Button(frame, text=msg.ME_DELETE, command=self._removeModule).pack()

    def _removeModule(self):
        self.page.remove(self.module)
        self.main.showPage(self.main.page_frame)
        self.close()

    def _updateModule(self):
        if "info_lines" in self.var_names.keys():
            lines = self.vars[self.var_names["info_lines"]].get()
            param_tag = self.module.find("param[@name='info_lines']")
            if param_tag is not None:
                param_tag.set("value", str(lines))
            else:
                et.SubElement(
                    self.module,
                    "param",
                    {"name": "info_lines",
                     "value": lines
                    }
                )

        if "size" in self.var_names.keys():
            size_name = self.vars[self.var_names["size"]].get()
            size_dict = {
                msg.PDF_SINGLE: page.SINGLE,
                msg.PDF_WIDE: page.WIDE,
                msg.PDF_DOUBLE: page.DOUBLE,
                msg.PDF_QUART: page.QUART,
                msg.PDF_TRIPLE: page.TRIPLE,
                msg.PDF_BIG: page.BIG,
                msg.PDF_FULL: page.FULL,
                msg.PDF_HALF: page.HALF
            }

            size = size_dict[size_name]
            self.module.set("size", size)

        self.main.showPage(self.main.page_frame)
        self.close()
 
    # add a new module ... 
    def _addModule(self):
        self._defineModule()
        self.main.addModule(self.module)
        self.main.showPage(self.main.page_frame)
        self.close()

    # retrieve the module ... 
    def _getModule(self):
        
        row = self.row
        col = self.col
        id = self.main.grid[self.main.active_page-1][col][row]
        
        module = self.page.find("module[@id='"+str(id)+"']")
        return module

    # retrieve available space 
    def _getSpace(self):
        """ gets available space for one and two column modules ..
        return: (h1,h2)
        """
        height_1 = 0
        height_1_lock = False
        height_2 = 0
        height_2_lock = False
        row = self.row
        col = self.col

        m_id = 0
        if self.module is not None: m_id = int(self.module.get("id"))

        while row <= 3 and not height_1_lock:
            id1 = self.main.grid[self.main.active_page-1][col][row]
            if id1 == 0 or id1 == m_id:
                height_1 += 1
            else:
                height_1_lock = True
            if col <= 2:
                id2 = self.main.grid[self.main.active_page-1][col+1][row]
                if ((id2 == 0 or id2 == m_id)
                    and (id1 == 0 or id1 == m_id)
                    and not height_2_lock
                ):
                    height_2 += 1
                else:
                    height_2_lock = True
            row += 1        

        return height_1, height_2

    # module type changed ... 
    def _modTypeChanged(self, name, e, m):
        selected = self.vars[name].get()
       
        try:  
            frame = self.widgets["options"]
        except KeyError:
            frame = None

        if frame: 
            # cleanup ... 
            widgets = frame.winfo_children()
            for widget in widgets:
                widget.destroy()

            row = str(self.row)
            col = str(self.col)

            sizes = self._potentialSizes()

            if selected == msg.PDF_ATTRIBUTES:
                if msg.PDF_DOUBLE in sizes:
                    sizes = [msg.PDF_DOUBLE]
                else:
                    sizes = [""]

            if selected == msg.PDF_EWT:
                if msg.PDF_SINGLE in sizes:
                    sizes = [msg.PDF_SINGLE]
                else:
                    sizes = [""]

            size = tk.StringVar()
            self.vars[str(size)] = size
            self.var_names["size"] = str(size)
            size_button = tk.OptionMenu(
                frame,
                size,
                *tuple(sizes)
            )
            size.set(sizes[0])
            size_button.pack(fill=tk.X)

            if selected == msg.PDF_TRAITS: 
                """
                trait_type = "all", 
                info_lines = 1, 
                start_index = 0
                """
                trait_types = [
                    msg.PDF_ALL_TRAITS,
                    msg.PDF_POSITIVE_TRAITS,
                    msg.PDF_NEGATIVE_TRAITS
                ]
                trait_type = tk.StringVar()
                self.vars[str(trait_type)] = trait_type
                self.var_names["trait_type"] = str(trait_type)
                trait_type_button = tk.OptionMenu(
                    frame,
                    trait_type,
                    *tuple(trait_types)
                )
                trait_type.set(trait_types[0])
                trait_type_button.pack()

                info_lines = tk.StringVar()
                self.vars[str(info_lines)] = info_lines
                self.var_names["info_lines"] = str(info_lines)
                info_lines.set("0")
                info_lines_frame = tk.Frame(frame)
                info_lines_label = tk.Label(
                    info_lines_frame,
                    text=msg.ME_TEXTLINES
                )
                info_lines_label.pack(side=tk.LEFT)
                info_lines_spinner = tk.Spinbox(
                    frame,
                    from_=0,
                    to=5,
                    textvariable=info_lines,
                    width=2)
                info_lines_spinner.pack(side=tk.LEFT)
                info_lines_frame.pack(fill=tk.X, expand=1)
                
                pass

            if selected == msg.PDF_SKILLS:
                skill_types = [
                    msg.PDF_SKILLS_ALL,
                    msg.PDF_SKILLS_ACTIVE,
                    msg.PDF_SKILLS_PASSIVE,
                    msg.PDF_SKILLS_KNOWLEDGE,
                    msg.PDF_SKILLS_LANGUAGE
                ]

                skill_type = tk.StringVar()
                self.vars[str(skill_type)] = skill_type
                self.var_names["skill_type"] = str(skill_type)
                skill_type_button = tk.OptionMenu(
                    frame,
                    skill_type,
                    *tuple(skill_types)
                )
                skill_type.set(skill_types[0])
                skill_type_button.pack()

            if selected == msg.PDF_WEAPONS:
                variants = [
                    msg.PDF_ALL_WEAPONS,
                    msg.PDF_MELEE,
                    msg.PDF_GUNS,
                    msg.PDF_AMMO
                ]

                variant = tk.StringVar()
                self.vars[str(variant)] = variant
                self.var_names["variant"] = str(variant)
                variant_button = tk.OptionMenu(frame, variant, *tuple(variants))
                variant.set(variants[0])
                variant_button.pack()

                equipped = tk.IntVar()
                self.vars[str(equipped)] = equipped
                self.var_names["equipped"] = str(equipped)
                equipped.set(0)

                tk.Checkbutton(
                    frame,
                    text=msg.ME_EQUIPPED_WEAPONS,
                    variable=equipped,
                    offvalue=0,
                    onvalue=1
                ).pack()

                amount = tk.IntVar()
                self.vars[str(amount)] = amount
                self.var_names["amount"] = str(amount)
                amount.set(0)

                tk.Checkbutton(
                    frame,
                    text=msg.ME_SHOW_QUANTITY,
                    variable=amount,
                    offvalue=0,
                    onvalue=1
                ).pack()

                info_lines = tk.StringVar()
                self.vars[str(info_lines)] = info_lines
                self.var_names["info_lines"] = str(info_lines)
                info_lines.set("0")
                info_lines_frame = tk.Frame(frame)
                info_lines_label = tk.Label(
                    info_lines_frame,
                    text=msg.ME_TEXTLINES
                )
                info_lines_label.pack(side=tk.LEFT)
                info_lines_spinner = tk.Spinbox(
                    frame,
                    from_=0,
                    to=5,
                    textvariable=info_lines,
                    width=2
                )
                info_lines_spinner.pack(side=tk.LEFT)
                info_lines_frame.pack(fill=tk.X, expand=1)

            if selected == msg.PDF_EQUIPMENT:

                item_group = tk.StringVar()
                groups = [
                    msg.PDF_EQUIPMENT_ALL,
                    msg.PDF_EQUIPMENT_CLOTHING,
                    msg.PDF_EQUIPMENT_TOOLS,
                    msg.PDF_EQUIPMENT_BIOTECH,
                    msg.PDF_EQUIPMENT_MONEY
                ]
                self.vars[str(item_group)] = item_group
                self.var_names["item_group"] = str(item_group)
                item_group.set(groups[0])
                labelframe = tk.LabelFrame(frame, text="Gruppe wählen")
                tk.OptionMenu(labelframe, item_group, *groups).pack(fill=tk.X)
                labelframe.pack(fill=tk.X)

                # condense items selection ... 
                condensed = tk.IntVar()
                self.vars[str(condensed)] = condensed
                self.var_names["condensed"] = str(condensed)
                condensed.set(0)
                tk.Checkbutton(
                    frame,
                    text=msg.ME_CONDENSE,
                    variable=condensed,
                    offvalue=0,
                    onvalue=1,
                    anchor=tk.W
                ).pack(fill=tk.X, expand=1)

                # show only equipped stuff selection
                equipped = tk.IntVar()
                self.vars[str(equipped)] = equipped
                self.var_names["equipped"] = str(equipped)
                equipped.set(0)
                tk.Checkbutton(
                    frame,
                    text=msg.ME_EQUIPPED_STUFF,
                    variable=equipped,
                    offvalue=0,
                    onvalue=1,
                    anchor=tk.W
                ).pack(fill=tk.X, expand=1)

                # display content selection
                content = tk.IntVar()
                self.vars[str(content)] = content
                self.var_names["content"] = str(content)
                content.set(0)
                tk.Checkbutton(
                    frame,
                    text=msg.ME_BAG_CONTENTS,
                    variable=content,
                    offvalue=0,
                    onvalue=1,
                    anchor=tk.W
                ).pack(fill=tk.X, expand=1)

                # display weapons selection
                display_weapons = tk.IntVar()
                self.vars[str(display_weapons)] = display_weapons
                self.var_names["display_weapons"] = str(display_weapons)
                display_weapons.set(0)
                tk.Checkbutton(
                    frame,
                    text=msg.ME_SHOW_WEAPONS,
                    variable=display_weapons,
                    offvalue=0,
                    onvalue=1,
                    anchor=tk.W
                ).pack(fill=tk.X, expand=1)

                # use item_id selector
                use_item_id = tk.IntVar()
                self.vars[str(use_item_id)] = use_item_id
                self.var_names["use_item_id"] = str(use_item_id)
                use_item_id.set(0)
                use_item_id_button = tk.Checkbutton(
                    frame,
                    text=msg.ME_ONLY_BAG,
                    variable=use_item_id,
                    offvalue=0,
                    onvalue=1,
                    anchor=tk.NW,
                    justify=tk.LEFT
                )
                use_item_id_button.pack(fill=tk.X, expand=1)

                # select items that are bags/containers ... 
                items = self.main.char.getItems()
                containers = [
                    it.CLOTHING,
                    it.BAG,
                    it.CONTAINER,
                    it.BOX,
                    it.TOOLS,
                    it.HARNESS]
                self.vars["bags"] = []
                for item in items:
                    if item.get("type") in containers:
                        container = item.find("container")
                        if container is not None: 
                            item_id = item.get("id")
                            item_name = item.get("name")
                            self.vars["bags"].append(item_id+": "+item_name)

                if len(self.vars["bags"]) == 0:
                    use_item_id_button.config(state=tk.DISABLED)
                else:                          
                    bag_lists = self.vars["bags"]
                    bag_list = tk.StringVar()
                    self.vars[str(bag_list)] = bag_list
                    self.var_names["bag_list"] = str(bag_list)
                    bag_list_button = tk.OptionMenu(
                        frame,
                        bag_list,
                        *tuple(bag_lists)
                    )
                    bag_list.set(bag_lists[0])
                    bag_list_button.pack()

                # how many info_lines
                info_lines = tk.StringVar()
                self.vars[str(info_lines)] = info_lines
                self.var_names["info_lines"] = str(info_lines)
                info_lines.set("0")
                info_lines_frame = tk.Frame(frame)
                info_lines_label = tk.Label(
                    info_lines_frame,
                    text=msg.ME_TEXTLINES
                )
                info_lines_label.pack(side=tk.LEFT)
                info_lines_spinner = tk.Spinbox(
                    frame,
                    from_=0,
                    to=5,
                    textvariable=info_lines,
                    width=2
                )
                info_lines_spinner.pack(side=tk.LEFT)

                # show weight
                show_weight = tk.IntVar()
                self.vars[str(show_weight)] = show_weight
                self.var_names["show_weight"] = str(show_weight)
                show_weight.set(0)
                tk.Checkbutton(
                    info_lines_frame,
                    text=msg.ME_SHOW_WEIGHT,
                    variable=show_weight,
                    offvalue=0,
                    onvalue=1
                ).pack(side=tk.LEFT)

                # show value
                show_value = tk.IntVar()
                self.vars[str(show_value)] = show_value
                self.var_names["show_value"] = str(show_value)
                show_value.set(0)
                tk.Checkbutton(
                    info_lines_frame,
                    text=msg.ME_SHOW_VALUE,
                    variable=show_value,
                    offvalue=0,
                    onvalue=1
                ).pack(side=tk.LEFT)

                info_lines_frame.pack(fill=tk.X, expand=1)

                # add traces (when everything exists) ...
                condensed.trace("w", self._equipmentOptions)
                equipped.trace("w", self._equipmentOptions)
                content.trace("w", self._equipmentOptions)
                use_item_id.trace("w", self._equipmentOptions)

            if selected == msg.PDF_CONTACTS:
                contact_types = [
                    msg.PDF_ALL_CONTACTS,
                    msg.PDF_FRIENDS,
                    msg.PDF_ENEMIES
                ]

                contact_type = tk.StringVar()
                self.vars[str(contact_type)] = contact_type
                self.var_names["contact_type"] = str(contact_type)
                contact_type_button = tk.OptionMenu(
                    frame,
                    contact_type,
                    *tuple(contact_types)
                )
                contact_type.set(contact_types[0])
                contact_type_button.pack()

                info_lines = tk.StringVar()
                self.vars[str(info_lines)] = info_lines
                self.var_names["info_lines"] = str(info_lines)
                info_lines.set("0")
                info_lines_frame = tk.Frame(frame)
                info_lines_label = tk.Label(
                    info_lines_frame,
                    text=msg.ME_TEXTLINES
                )
                info_lines_label.pack(side=tk.LEFT)
                info_lines_spinner = tk.Spinbox(
                    frame,
                    from_=0,
                    to=5,
                    textvariable=info_lines,
                    width=2
                )
                info_lines_spinner.pack(side=tk.LEFT)
                info_lines_frame.pack(fill=tk.X, expand=1)

            if selected == msg.PDF_NOTES:
                notes = self.main.char.getNotes()
                entries = []
                for note in notes:
                    id = note.get("id", "")
                    name = note.get("name", "")

                    entries.append(id+": "+name)

                if entries:
                    var = tk.StringVar()
                    var.set(msg.ME_NOT_SELECTED)
                    var.trace("w", self._notesEdited)
                    self.vars["id"] = var

                    sub_frame = tk.LabelFrame(frame, text=msg.ME_NOTES)

                    button = tk.OptionMenu(
                        sub_frame,
                        var,
                        *entries
                    )
                    button.pack(fill=tk.X)
                    sub_frame.pack(fill=tk.X)

                title = tk.StringVar()
                self.vars["title"] = title
                title_frame = tk.LabelFrame(frame, text=msg.ME_TITLE)
                entry = tk.Entry(title_frame, textvariable=title)
                entry.pack(fill=tk.X)
                title_frame.pack(fill=tk.X)
                title.trace("w", self._notesEdited)

            if selected == msg.PDF_IMAGE:
                pass

    # create a list of potential module sizes
    def _potentialSizes(self):
        sizes = []
        for height in range(self.space[0]+1):
            if height == 1: 
                sizes.append(msg.PDF_SINGLE)
                if height <= self.space[1]:
                    sizes.append(msg.PDF_WIDE)
            if height == 2: 
                sizes.append(msg.PDF_DOUBLE)
                if height <= self.space[1]:
                    sizes.append(msg.PDF_QUART)
            if height == 3: 
                sizes.append(msg.PDF_TRIPLE)
                if height <= self.space[1]:
                    sizes.append(msg.PDF_BIG)
            if height == 4: 
                sizes.append(msg.PDF_FULL)
                if height <= self.space[1]:
                    sizes.append(msg.PDF_HALF)
        return sizes

    # make sure that only equipmentoptions are selected that can be combined ... 
    def _equipmentOptions(self, name, e, m):
        if name == self.var_names["condensed"]:
            if self.vars[name].get() == 1: 
                self.vars[self.var_names["equipped"]].set(0)
                self.vars[self.var_names["content"]].set(0)
                self.vars[self.var_names["use_item_id"]].set(0)

        if name == self.var_names["equipped"]:
            if self.vars[name].get() == 1:  
                self.vars[self.var_names["condensed"]].set(0)
                self.vars[self.var_names["use_item_id"]].set(0)

        if name == self.var_names["content"]: 
            if self.vars[name].get() == 1: 
                self.vars[self.var_names["condensed"]].set(0)
                self.vars[self.var_names["use_item_id"]].set(0)

        if name == self.var_names["use_item_id"]: 
            if self.vars[name].get() == 1: 
                self.vars[self.var_names["condensed"]].set(0)
                self.vars[self.var_names["equipped"]].set(0)
                self.vars[self.var_names["content"]].set(0)

    def _notesEdited(self, n, e, m):
        title = self.vars.get("title")
        id = self.vars.get("id")
        if title and id:
            if str(title) == n:
                if title.get() != "":
                    id.set(msg.ME_NOT_SELECTED)
            else:
                if id.get() != msg.ME_NOT_SELECTED:
                    title.set("")

    # this creates the et.Element for one module based on the current selection
    def _defineModule(self):

        mod_dict = {
            msg.PDF_ATTRIBUTES: page.MOD_ATTRIBUTES,
            msg.PDF_TRAITS: page.MOD_TRAITS,
            msg.PDF_SKILLS: page.MOD_SKILLS,
            msg.PDF_EQUIPMENT: page.MOD_EQUIPMENT,
            msg.PDF_WEAPONS: page.MOD_WEAPONS,
            msg.PDF_CONTACTS: page.MOD_CONTACTS,
            msg.PDF_EWT: page.MOD_EWT,
            msg.PDF_IMAGE: page.MOD_IMAGE,
            msg.PDF_NOTES: page.MOD_NOTES
        }
        
        size_dict = {
            msg.PDF_SINGLE: page.SINGLE,
            msg.PDF_WIDE: page.WIDE,
            msg.PDF_DOUBLE: page.DOUBLE,
            msg.PDF_QUART: page.QUART,
            msg.PDF_TRIPLE: page.TRIPLE,
            msg.PDF_BIG: page.BIG,
            msg.PDF_FULL: page.FULL,
            msg.PDF_HALF: page.HALF
        }

        trait_dict = {
            msg.PDF_ALL_TRAITS: "all",
            msg.PDF_POSITIVE_TRAITS: "positive",
            msg.PDF_NEGATIVE_TRAITS: "negative"
        }

        skill_dict = {
            msg.PDF_SKILLS_ALL: "all",
            msg.PDF_SKILLS_ACTIVE: "active",
            msg.PDF_SKILLS_PASSIVE: "passive",
            msg.PDF_SKILLS_KNOWLEDGE: "knowledge",
            msg.PDF_SKILLS_LANGUAGE: "lang"
        }

        contact_dict = {
            msg.PDF_ALL_CONTACTS: "all",
            msg.PDF_FRIENDS: "friends",
            msg.PDF_ENEMIES: "enemies"
        }

        weapons_dict = {
            msg.PDF_ALL_WEAPONS: "all",
            msg.PDF_MELEE: "melee",
            msg.PDF_GUNS: "guns",
            msg.PDF_AMMO: "ammo"
        }

        module = self.vars[self.var_names["module"]].get()
        size_var = self.vars[self.var_names["size"]].get()

        mod_type = mod_dict[module]
        size = size_dict[size_var]
        row = str(self.row)
        col = str(self.col)
        id = str(self.main.getHighestModuleId()+1)

        self.module = et.Element(
            "module",
            {"type": mod_type,
             "row": row,
             "col": col,
             "id": id,
             "size": size
             }
        )

        if mod_type == page.MOD_TRAITS: 
            trait_var = self.vars[self.var_names["trait_type"]].get()
            trait_type = trait_dict[trait_var]
            info_lines = str(self.vars[self.var_names["info_lines"]].get())

            info_lines_var = self.vars[self.var_names["info_lines"]].get()
            et.SubElement(
                self.module,
                "param",
                {"name": "trait_type",
                 "value": trait_type
                 }
            )
            et.SubElement(
                self.module,
                "param",
                {"name": "info_lines",
                 "value": info_lines
                 }
            )

        elif mod_type == page.MOD_SKILLS: 
            skill_var = self.vars[self.var_names["skill_type"]].get()
            skill_type = skill_dict[skill_var]
            et.SubElement(
                self.module,
                "param",
                {"name": "skill_type",
                 "value": skill_type
                 }
            )

        elif mod_type == page.MOD_EQUIPMENT:
            use_item_id_var = self.vars[self.var_names["use_item_id"]].get()
            condensed_var = self.vars[self.var_names["condensed"]].get()
            equipped_var = self.vars[self.var_names["equipped"]].get()
            content_var = self.vars[self.var_names["content"]].get()
            show_weapons_var = self.vars[self.var_names["display_weapons"]].get()
            show_weight_var = self.vars[self.var_names["show_weight"]].get()
            show_value_var = self.vars[self.var_names["show_value"]].get()
            groups_var = self.vars[self.var_names["item_group"]].get()

            info_lines_var = self.vars[self.var_names["info_lines"]].get()
            et.SubElement(
                self.module,
                "param",
                {"name": "info_lines",
                 "value": str(info_lines_var)
                 }
            )

            if groups_var != msg.PDF_EQUIPMENT_ALL:
                if groups_var == msg.PDF_EQUIPMENT_TOOLS:
                    item_type = it.TOOLS
                elif groups_var == msg.PDF_EQUIPMENT_CLOTHING:
                    item_type = [
                        it.CLOTHING,
                        it.ARMOR,
                        it.HARNESS
                    ]
                elif groups_var == msg.PDF_EQUIPMENT_BIOTECH:
                    item_type = [
                        it.IMPLANT,
                        it.PROSTHESIS,
                        it.IMPLANT_PART
                    ]
                else:
                    item_type = [it.MONEY]

                item_type = ",".join(item_type)

                et.SubElement(
                    self.module,
                    "param",
                    {"name": "item_type",
                     "value": item_type
                     }
                )

            if show_weight_var == 1:
                et.SubElement(
                    self.module,
                    "param",
                    {"name": "show_weight",
                     "value": "True"
                     }
                )
            if show_value_var == 1:
                et.SubElement(
                    self.module,
                    "param",
                    {"name": "show_value",
                     "value": "True"
                     }
                )

            if use_item_id_var == 1:
                bag_var = self.vars[self.var_names["bag_list"]].get() 
                item_id = bag_var.split(":")[0]
                et.SubElement(
                    self.module,
                    "param",
                    {"name": "item_id",
                     "value": item_id
                     }
                )
            elif condensed_var == 1:
                et.SubElement(
                    self.module,
                    "param",
                    {"name": "condensed",
                     "value": "True"
                     }
                )
            else:
                if equipped_var == 1: 
                    et.SubElement(
                        self.module,
                        "param",
                        {"name": "equipped",
                         "value": "True"
                         }
                    )
                if content_var == 1:
                    et.SubElement(
                        self.module,
                        "param",
                        {"name": "content",
                         "value": "True"
                         }
                    )
                if show_weapons_var == 0:
                    weapons = [
                        it.CLUBS,
                        it.BLADES,
                        it.STAFFS,
                        it.PISTOLS,
                        it.REVOLVERS,
                        it.RIFLES,
                        it.RIFLES_SA,
                        it.SHOT_GUNS,
                        it.SHOT_GUNS_SA,
                        it.BLASTER
                    ]
                    weapons_string = ",".join(weapons)
                    et.SubElement(
                        self.module,
                        "param",
                        {"name": "exclude",
                         "value": weapons_string
                         }
                    )

        elif mod_type == page.MOD_CONTACTS:
            contact_var = self.vars[self.var_names["contact_type"]].get()
            contact_type = contact_dict[contact_var]
            info_lines_var = self.vars[self.var_names["info_lines"]].get()

        elif mod_type == page.MOD_WEAPONS:
            variant_var = self.vars[self.var_names["variant"]].get()
            variant = weapons_dict[variant_var]
            et.SubElement(self.module,
                          "param",
                          {"name": "variant",
                           "value": str(variant)
                           }
                          )

            info_lines_var = self.vars[self.var_names["info_lines"]].get()
            et.SubElement(
                self.module,
                "param",
                {"name": "info_lines",
                 "value": str(info_lines_var)
                 }
            )

        elif mod_type == page.MOD_NOTES:
            selected_note = self.vars.get("id")
            title = self.vars.get("title")
            note_id = ""
            if selected_note:
                id_value = selected_note.get()
                if id_value != msg.ME_NOT_SELECTED:
                    note_id = id_value.split(":")[0]
                    et.SubElement(
                        self.module,
                        "param",
                        {"name": "note_id",
                         "value": note_id
                         }
                    )
            if title:
                title = title.get()
                if title:
                    et.SubElement(
                        self.module,
                        "param",
                        {"name": "title",
                         "value": title
                         }
                    )

    def close(self):
        self.main.open_windows["mod_ed"] = 0
        self.destroy()
