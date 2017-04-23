import tk_ as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
import config
from PIL import ImageTk
import re
from tooltip import ToolTip
import xml.etree.ElementTree as et

msg = config.Messages()

"""
FOR LATER USE 
members = [attr for attr in dir(msg) if not attr.startswith("__")]
print(members)
"""


class ExpansionScreen(tk.Frame):
    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.char = app.char
        self.settings = app.settings
        self.data = {}
        self.widgets = {}

        self.expansion = self._newExpansion()

        self.rowconfigure(1, weight=100)
        self.columnconfigure(0, weight=100)
        self.toolbar = tk.Frame(self)
        self.toolbar.grid(row=0, column=0, sticky=tk.NSEW)
        self.showToolbar(self.toolbar)
        self.frame = tk.Frame(self)
        self.frame.grid(row=1, column=0, sticky=tk.NSEW)

        trait_frame = self.showTraits(self.frame)
        skill_frame = self.showSkills(self.frame)
        item_frame = self.showItems(self.frame)
        trait_frame.place(
            relx=0,
            rely=0,
            relwidth=1/3,
            relheight=1,
            anchor=tk.NW
        )
        skill_frame.place(
            relx=1/3,
            rely=0,
            relwidth=1/3,
            relheight=1,
            anchor=tk.NW
        )
        item_frame.place(
            relx=2/3,
            rely=0,
            relwidth=1/3,
            relheight=1,
            anchor=tk.NW
        )

        self._select()
        
    def showTraits(self, frame):
        trait_frame = tk.LabelFrame(frame, text=msg.EX_TRAITS)
        list_frame = tk.Frame(trait_frame)
        self.widgets["traits"] = trait_list = tk.Listbox(
            list_frame,
            width=1,
            height=1
        )
        trait_list.bind("<<ListboxSelect>>", self._select)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=trait_list.yview)
        trait_list.config(yscrollcommand=scroll.set)
        trait_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack(fill=tk.BOTH, expand=1)
        new_trait = tk.Button(
            trait_frame,
            text=msg.EX_NEW,
            command=self._addTrait
        )
        new_trait.pack(fill=tk.X)
        self.widgets["edit_trait"] = edit_trait = tk.Button(
            trait_frame,
            text=msg.EX_EDIT,
            command=self._editTrait
        )
        edit_trait.pack(fill=tk.X)
        self.widgets["del_trait"] = del_trait = tk.Button(
            trait_frame,
            text=msg.EX_DEL,
            command=self._delTrait
        )
        del_trait.pack(fill=tk.X)

        return trait_frame

    def updateTraits(self):
        listbox = self.widgets["traits"]
        skills = self.expansion.findall(".//trait")
        listbox.delete(0, tk.END)
        l = [s.get("name") for s in skills]
        listbox.insert(0, *l)

    def showSkills(self, frame):
        skill_frame = tk.LabelFrame(frame, text=msg.EX_SKILLS)
        list_frame = tk.Frame(skill_frame)
        self.widgets["skills"] = skill_list = tk.Listbox(
            list_frame,
            width=1,
            height=1
        )
        skill_list.bind("<<ListboxSelect>>", self._select)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=skill_list.yview)
        skill_list.config(yscrollcommand=scroll.set)
        skill_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack(fill=tk.BOTH, expand=1)

        add_skill = tk.Button(
            skill_frame,
            text=msg.EX_NEW,
            command=self._addSkill
        )
        add_skill.pack(fill=tk.X)

        self.widgets["sub_skill"] = sub_skill = SkillCopy(
            skill_frame,
            app=self.app
        )
        sub_skill.pack(fill=tk.X)

        self.widgets["edit_skill"] = edit_skill = tk.Button(
            skill_frame,
            text=msg.EX_EDIT,
            command=self._editSkill
        )
        edit_skill.pack(fill=tk.X)

        self.widgets["del_skill"] = del_skill = tk.Button(
            skill_frame,
            text=msg.EX_DEL,
            command=self._delSkill
        )
        del_skill.pack(fill=tk.X)

        return skill_frame

    def updateSkills(self):
        listbox = self.widgets["skills"]
        skills = self.expansion.findall(".//skill")
        listbox.delete(0, tk.END)
        l = [s.get("name") for s in skills]
        listbox.insert(0, *l)

    def showItems(self, frame):
        item_frame = tk.LabelFrame(frame, text=msg.EX_ITEMS)
        list_frame = tk.Frame(item_frame)
        self.widgets["items"] = item_list = tk.Listbox(
            list_frame,
            width=1,
            height=1
        )
        item_list.bind("<<ListboxSelect>>", self._select)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=item_list.yview)
        item_list.config(yscrollcommand=scroll.set)
        item_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack(fill=tk.BOTH, expand=1)
        new_item = tk.Button(
            item_frame,
            text=msg.EX_NEW,
            command=self._addItem
        )
        new_item.pack(fill=tk.X)
        self.widgets["edit_item"] = edit_item = tk.Button(
            item_frame,
            text=msg.EX_EDIT,
            command=self._editItem
        )
        edit_item.pack(fill=tk.X)
        self.widgets["del_item"] = del_item = tk.Button(
            item_frame,
            text=msg.EX_DEL,
            command=self._delItem
        )
        del_item.pack(fill=tk.X)

        self.updateItems()
        return item_frame

    def updateItems(self):
        listbox = self.widgets["items"]
        items = self.expansion.findall(".//item")
        listbox.delete(0, tk.END)
        l = [i.get("name") for i in items]
        listbox.insert(0, *l)

    def _select(self, event=None):
        """ enable and disable buttons based on selection of listboxes """

        if event:
            listbox = event.widget
            selection = listbox.curselection()
        else:
            listbox = 1
            selection = []

        if listbox == self.widgets.get("traits") or not event:
            if len(selection) < 1:
                self.widgets.get("edit_trait").config(state=tk.DISABLED)
                self.widgets.get("del_trait").config(state=tk.DISABLED)
            else:
                self.widgets.get("edit_trait").config(state=tk.NORMAL)
                self.widgets.get("del_trait").config(state=tk.NORMAL)

        if listbox == self.widgets.get("skills") or not event:
            if len(selection) < 1:
                self.widgets.get("edit_skill").config(state=tk.DISABLED)
                self.widgets.get("del_skill").config(state=tk.DISABLED)

                name_entry = self.widgets.get("sub_skill").name_entry
                if str(self.focus_get()) != str(name_entry):
                    self.widgets.get("sub_skill").config(state=tk.DISABLED)
            else:
                self.widgets.get("edit_skill").config(state=tk.NORMAL)
                self.widgets.get("del_skill").config(state=tk.NORMAL)

                name = listbox.get(selection)
                skill = self.expansion.find(".//skill[@name='" + name + "']")
                self.widgets.get("sub_skill").updateSource(skill)
                self.widgets.get("sub_skill").config(state=tk.NORMAL)

        if listbox == self.widgets.get("items") or not event:
            if len(selection) < 1:
                self.widgets.get("edit_item").config(state=tk.DISABLED)
                self.widgets.get("del_item").config(state=tk.DISABLED)
            else:
                self.widgets.get("edit_item").config(state=tk.NORMAL)
                self.widgets.get("del_item").config(state=tk.NORMAL)

    def showToolbar(self, frame):

        exp_ops = [
            (msg.EX_TT_NEW, "img/tpl_new.png", self._newExpansion),
            (msg.EX_TT_LOAD, "img/tpl_load.png", self._loadExpansion),
            (msg.EX_TT_SAVE, "img/tpl_save.png", self._saveExpansion)
        ]

        new_icon = ImageTk.PhotoImage(file="img/tpl_new.png")
        load_icon = ImageTk.PhotoImage(file="img/tpl_load.png")
        save_icon = ImageTk.PhotoImage(file="img/tpl_save.png")

        exp = tk.LabelFrame(frame, text="Expansion")
        for op in exp_ops:
            img = ImageTk.PhotoImage(file=op[1])
            self.widgets[op[0]] = button = tk.Button(
                exp,
                text=op[0],
                image=img,
                command=op[2],
            )
            if op[0] == msg.EX_TT_SAVE:
                button.config(state=tk.DISABLED)
            tt = ToolTip(button, op[0])
            button.image = img
            button.pack(side=tk.LEFT)
        exp.pack(side=tk.LEFT)

        tk.Label(frame, text=" ").pack(side=tk.LEFT)

        name_frame = tk.LabelFrame(frame, text=msg.EX_NAME)
        self.data["name"] = name = tk.StringVar()
        name_entry = tk.Entry(name_frame, textvariable=name)
        name.trace("w", lambda n, e, m: self._updateName())
        name_entry.pack(fill=tk.BOTH, expand=1)
        name_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

    def _updateName(self):
        name = self.data.get("name").get()
        if len(name) < 1:
            self.widgets[msg.EX_TT_SAVE].config(state=tk.DISABLED)
        else:
            self.widgets[msg.EX_TT_SAVE].config(state=tk.NORMAL)


        print(name)
        root = self.expansion.getroot()
        root.set("name", name)

    def _addItem(self, event=None):
        if self.app.open_windows["itemedit"] != 0:
            self.app.open_windows["itemedit"].close()
        self.app.open_windows["itemedit"] = ItemEditor(
            self.app.main,
            self.app,
            None
        )

    def _editItem(self, event=None):
        listbox = self.widgets["items"]
        selected = listbox.curselection()
        if len(selected) != 1:
            return
        name = listbox.get(selected[0])
        item = self.expansion.find(".//item[@name='"+name+"']")

        if self.app.open_windows["itemedit"] != 0:
            self.app.open_windows["itemedit"].close()
        self.app.open_windows["itemedit"] = ItemEditor(
            self.app.main,
            self.app,
            item
        )

    def _delItem(self):
        listbox = self.widgets["items"]
        selected = listbox.curselection()
        if len(selected) != 1:
            return
        name = listbox.get(selected[0])
        items = self.expansion.find(".//items")
        item = items.find(".//item[@name='"+name+"']")

        if item is not None:
            items.remove(item)
            self.updateItems()

    def _addTrait(self, event=None):
        if self.app.open_windows["trait"] != 0:
            self.app.open_windows["trait"].close()
        self.app.open_windows["trait"] = TraitEditor(
            self.app.main,
            self.app,
            None
        )

    def _editTrait(self):
        listbox = self.widgets["traits"]
        selected = listbox.curselection()
        if len(selected) != 1:
            return
        name = listbox.get(selected[0])
        trait = self.expansion.find(".//trait[@name='"+name+"']")

        if self.app.open_windows["trait"] != 0:
            self.app.open_windows["trait"].close()
        self.app.open_windows["trait"] = TraitEditor(
            self.app.main,
            self.app,
            trait
        )

    def _delTrait(self):
        listbox = self.widgets["traits"]
        selected = listbox.curselection()
        if len(selected) != 1:
            return
        name = listbox.get(selected[0])
        traits = self.expansion.find(".//traits")
        trait = traits.find(".//trait[@name='"+name+"']")

        if trait is not None:
            traits.remove(trait)
            self.updateTraits()

    def _addSkill(self):
        if self.app.open_windows["skill"] != 0:
            self.app.open_windows["skill"].close()
        self.app.open_windows["skill"] = SkillEditor(
            self.app.main,
            self.app,
            None
        )

    def _editSkill(self):
        listbox = self.widgets["skills"]
        selected = listbox.curselection()
        if len(selected) != 1:
            return
        name = listbox.get(selected[0])
        skill = self.expansion.find(".//skill[@name='"+name+"']")

        if self.app.open_windows["skill"] != 0:
            self.app.open_windows["skill"].close()
        self.app.open_windows["skill"] = SkillEditor(
            self.app.main,
            self.app,
            skill
        )

    def _delSkill(self):
        listbox = self.widgets["skills"]
        selected = listbox.curselection()
        if len(selected) != 1:
            return
        name = listbox.get(selected[0])
        skills = self.expansion.find(".//skills")
        skill = skills.find(".//skill[@name='"+name+"']")

        if skill is not None:
            skills.remove(skill)
            self.updateSkills()

    @staticmethod
    def _newExpansion():
        """ creates a new expansion element tree """
        expansion = et.Element("expansion")
        et.SubElement(expansion, "meta")
        et.SubElement(expansion, "traits")
        et.SubElement(expansion, "skills")
        et.SubElement(expansion, "items")
        expansion = et.ElementTree(expansion)
        return expansion

    def _loadExpansion(self):
        """ loading an expansion from disk """
        options = {
            'defaultextension': '.xml',
            'filetypes': [('Template', '.xml')],
            'initialdir': './expansion',
            'initialfile': 'template.xml',
            'parent': self,
            'title': msg.EX_LOAD,
        }
        filename = tkfd.askopenfilename(**options)
        if filename:
            with open(filename, mode="rb") as file:
                expansion = et.parse(file)
                root = expansion.getroot()
                if root.tag == "expansion":
                    self.expansion = expansion
                    self.updateTraits()
                    self.updateSkills()
                    self.updateItems()
                    name = root.get("name")
                    if name:
                        self.data["name"].set("name")
        else:
            pass

    def _saveExpansion(self):
        """ save the current expansion to disk """

        options = {
            "defaultextension": ".xml",
            "filetypes": [("Expansion", ".xml")],
            "initialdir": "./expansion",
            "initialfile": "template.xml",
            "parent": self,
            "title": msg.EX_SAVE,
        }
        filename = tkfd.asksaveasfilename(**options)
        if filename:
            with open(filename, mode="wb") as file:
                self.expansion.write(
                    file,
                    encoding="utf-8",
                    xml_declaration=True
                )


class ItemEditor(tk.Toplevel):
    """ The item editor is used to create or modify items 
    
    Args:
        master (tk.Widget): parent widget
        app (Applicaion): program instance
        item (et.Element<item>): an item ot modify - None => new item
    """

    def __init__(
        self,
        master=None,
        app=None,
        item=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.app = app
        self.loaded_items = app.itemlist
        self.data = {}
        self.tt = {}

        self.minsize(250, 100)
        self.item = item

        if self.item is None:
            self.item = et.Element("item")
        else:
            self._readItem()

        self.existing_names = self._allNames()

        self.page = 1
        self._addName()

    def _allNames(self):
        items = self.app.itemlist.getAllItems()
        items = [i.get("name") for i in items]
        exp_items = self.app.module.expansion.findall(".//item")
        exp_items = [i.get("name") for i in exp_items]
        items = items + exp_items
        items = list(set(items))
        try:
            del items[items.index(self.item.get("name"))]
        except ValueError:
            pass
        return items

    def _readItem(self):
        """ distribute loaded item to the variables """

        # read basic data
        basic = ["name", "weight", "price", "avail", "parent"]
        for b in basic:
            self.data[b] = tk.StringVar()
            self.data[b].set(self.item.get(b))

        # retrieve the item type
        if self.item.get("type"):
            self.data["type"] = tk.StringVar()
            self.data["grp"] = tk.StringVar()
            self._updateTypes(item_type=self.item.get("type"))

        # check for quality range
        if self.item.get("quality"):
            self.data["min_q"] = tk.IntVar()
            self.data["max_q"] = tk.IntVar()

            min_q, max_q = self.item.get("quality").split(" ")
            self.data["min_q"].set(int(min_q))
            self.data["max_q"].set(int(max_q))

        # check for damage tag
        damage = self.item.find("damage")
        if damage is not None:
            self.data["damage"] = tk.StringVar()
            self.data["damage"].set(damage.get("value"))

        # read ammo tag
        ammo = self.item.find("ammo")
        if ammo is not None:
            self.data["ammo"] = tk.StringVar()
            self.data["ammo"].set(ammo.get("chambers"))

        # parse the option tags
        o_tags = self.item.findall("option")
        for option in o_tags:
            if option.get("name") == config.ItemTypes.OPTION_CALIBER:
                self.data["caliber"] = tk.StringVar()
                self.data["caliber"].set(option.get("values"))
            else:
                if not self.data.get("options"):
                    self.data["options"] = {}
                name = option.get("name")
                self.data["options"][name] = [
                    tk.IntVar(),
                    tk.StringVar()
                ]
                self.data["options"][name][0].set(1)
                values = option.get("values")
                if values:
                    self.data["options"][name][1].set(values)

        # read container information
        container = self.item.find("container")
        if container is not None:
            c_name = container.get("name", "")
            size = container.get("size", "0")
            limit = container.get("limit", "0")
            self.data["container"] = tk.IntVar()
            self.data["container"].set(1)
            self.data["container_name"] = tk.StringVar()
            self.data["container_name"].set(c_name)
            self.data["container_size"] = tk.StringVar()
            self.data["container_size"].set(size)
            self.data["container_limit"] = tk.StringVar()
            self.data["container_limit"].set(limit)

        # check if the item is sold in packs
        p_tags = self.item.findall("pack")
        self.data["packs"] = ""
        packs = []
        for pack in p_tags:
            q = pack.get("quantity")
            name = pack.get("name")
            q_label = re.findall("\(*\)", name)
            print(q_label)
            packs.append(q+": "+name)
        self.data["packs"] = "\n".join(packs)

        # get the description
        description = self.item.find("description")
        if description is not None:
            self.data["description"] = tk.StringVar()
            if description.text:
                self.data["description"].set(description.text)

    def _clear(self):
        """ clears the widget """

        widgets = self.winfo_children()
        for widget in widgets:
            widget.destroy()

    def _addName(self):
        """ First step: Setting a name and selecting an item type. """
        self._clear()

        if self.data.get("name"):
            name = self.data["name"]
        else:
            self.data["name"] = name = tk.StringVar()

        if self.item.get("name"):
            name.set(self.item.get("name"))

        name.trace("w", lambda n, e, m, var=name: self._checkName(var))

        name_frame = tk.LabelFrame(self, text=msg.NAME)
        self.name = tk.Entry(name_frame, textvariable=name)
        self.name.pack(fill=tk.X, expand=1)
        self.tt["name"] = ToolTip(self.name, msg.EX_TT_NAME, variant="info")
        name_frame.pack(fill=tk.X, expand=1)

        # item type is split into groups for better usability ...
        type_frame = tk.LabelFrame(self, text=msg.EX_ITEM_TYPE)
        ToolTip(type_frame, msg.EX_TT_TYPE, "info")
        groups = [
            msg.EX_IT_GRP_CLOTHING,
            msg.EX_IT_GRP_MELEE,
            msg.EX_IT_GRP_GUN,
            msg.EX_IT_GRP_OTHER,
            msg.EX_IT_GRP_BIOTECH,
        ]
        tk.Label(type_frame, text=msg.EX_IT_GRP).pack(fill=tk.X)
        if self.data.get("grp"):
            grp = self.data["grp"]
            start_group = grp.get()
        else:
            self.data["grp"] = grp = tk.StringVar()
            start_group = groups[0]

        self.grp = tk.OptionMenu(
            type_frame,
            grp,
            groups[0],
            *groups
        )
        self.grp.pack(fill=tk.X, expand=1)

        tk.Label(type_frame, text=msg.EX_IT_TYPE).pack(fill=tk.X)

        if self.data.get("type"):
            tp = self.data["type"]
        else:
            self.data["type"] = tp = tk.StringVar()

        self.tp = tk.OptionMenu(
            type_frame,
            tp,
            "",
            ""
        )
        self.tp.pack(fill=tk.X, expand=1)
        type_frame.pack(fill=tk.X, expand=1)

        grp.trace("w", lambda n, e, m, var=grp: self._updateTypes(var))
        grp.set(start_group)

        self._navigation()
        return True

    def _updateTypes(self, var=None, item_type=None):
        """ updating item type 
        
        Note: 
            This is used for two things - reading item type from existing
            item and switching item types during creation
            
            use only one of the args!
            
        Args:
            var (tk.StringVar): the changed variable [in trace mode]
            item_type (str): the stored item type from the <item>
            
        """

        clothing = [
            msg.EX_IT_CLOTHING,
            msg.EX_IT_HARNESS,
            msg.EX_IT_ARMOR,
            msg.EX_IT_BAG,
            msg.EX_IT_BOX,
            msg.EX_IT_CONTAINER,
        ]
        melee = [
            msg.EX_IT_NATURAL,
            msg.EX_IT_CLUB,
            msg.EX_IT_BLADE,
            msg.EX_IT_STAFF,
            msg.EX_IT_OTHER_MELEE,
        ]
        guns = [
            msg.EX_IT_REVOLVER,
            msg.EX_IT_PISTOL,
            msg.EX_IT_RIFLE,
            msg.EX_IT_SHOT_GUN,
            msg.EX_IT_RIFLE_SA,
            msg.EX_IT_SHOT_GUN_SA,
            msg.EX_IT_AUTOMATIC_WEAPON,
            msg.EX_IT_BLASTER,
            msg.EX_IT_BLASTER_SA,
            msg.EX_IT_CLIP,
            msg.EX_IT_AMMO,
        ]
        other = [
            msg.EX_IT_TOOLS,
            msg.EX_IT_MONEY,
            msg.EX_IT_SERVICE,
            msg.EX_IT_FOOD,
            msg.EX_IT_DRUG,
            msg.EX_IT_GENERIC
        ]
        biotech = [
            msg.EX_IT_IMPLANT,
            msg.EX_IT_PROSTHESIS,
            msg.EX_IT_IMPLANT_PART
        ]

        groups = {
            msg.EX_IT_GRP_CLOTHING: clothing,
            msg.EX_IT_GRP_MELEE: melee,
            msg.EX_IT_GRP_GUN: guns,
            msg.EX_IT_GRP_OTHER: other,
            msg.EX_IT_GRP_BIOTECH: biotech,
        }

        # this switches the item_type menu based on the selected group
        if var:
            try:
                selected = var.get()
                value = None
                if self.data.get("type"):
                    value = self.data["type"].get()
                if not value or value not in groups[selected]:
                    value = groups[selected][0]
                self.tp.set_menu(value, *groups[selected])

            except tk.TclError:
                pass

        # this translates the stored item type in the xml to the language
        # specific name used during editing.
        if item_type:
            types = {v: k for k, v in self._itemtypes().items()}
            item_type = types[item_type]
            self.data["type"].set(item_type)
            groups = [clothing, melee, guns, other, biotech]
            group_names = [
                msg.EX_IT_GRP_CLOTHING,
                msg.EX_IT_GRP_MELEE,
                msg.EX_IT_GRP_GUN,
                msg.EX_IT_GRP_OTHER,
                msg.EX_IT_GRP_BIOTECH,
            ]
            for i, group in enumerate(groups):
                if item_type in group:
                    self.data["grp"].set(group_names[i])
                    break

    def _checkName(self, var):
        """ Checking the name for validity 
        
        Updates field and tooltip as necessary.
        """

        name = var.get()
        invalid = re.findall("[\"\'&§<>]", name)

        if name in self.existing_names:
            self.name.config(style="invalid.TEntry")
            self.tt["name"].msg = msg.EX_TT_NAME_EXISTS
            self.tt["name"].variant = "error"
        elif len(invalid) > 0:
            self.name.config(style="invalid.TEntry")
            self.tt["name"].msg = msg.EX_TT_NAME_INVALID
            self.tt["name"].variant = "error"
        elif len(name) == 0:
            self.name.config(style="invalid.TEntry")
            self.tt["name"].msg = msg.EX_TT_NAME
            self.tt["name"].variant = "error"

        else:
            self.name.config(style="TEntry")
            self.tt["name"].msg = msg.EX_TT_NAME_OKAY
            self.tt["name"].variant = "okay"

    def _showName(self):
        """ Displays name and type """

        tk.Label(
            self,
            text=self.data["name"].get(),
            font="Arial 12 bold"
        ).pack()
        tk.Label(self, text=self.data["type"].get()).pack()

    def _addData(self):
        """ This screen is used to set basic data """

        self._clear()
        self._showName()

        if self.data.get("price"):
            price = self.data["price"]
        else: 
            self.data["price"] = price = tk.StringVar()
            price.set("0.01")
        if self.data.get("weight"):
            weight = self.data["weight"]
        else: 
            self.data["weight"] = weight = tk.StringVar()
            weight.set("1")
        if self.data.get("avail"):
            avail = self.data["avail"]
        else:
            self.data["avail"] = avail = tk.StringVar()
            avail.set("0")

        p_frame = tk.LabelFrame(self, text=msg.EX_ITEM_PRICE)
        self.p_entry = tk.Entry(p_frame, textvariable=price)
        self.tt["p"] = ToolTip(self.p_entry, msg.EX_TT_PRICE, "info")
        self.p_entry.pack(fill=tk.X, expand=1)
        p_frame.pack(fill=tk.X)

        w_frame = tk.LabelFrame(self, text=msg.EX_ITEM_WEIGHT)
        self.w_entry = tk.Entry(w_frame, textvariable=weight)
        self.tt["w"] = ToolTip(self.w_entry, msg.EX_TT_WEIGHT, "info")
        self.w_entry.pack(fill=tk.X, expand=1)
        w_frame.pack(fill=tk.X)
    
        a_frame = tk.LabelFrame(self, text=msg.EX_ITEM_AVAIL)
        self.a_entry = tk.Entry(a_frame, textvariable=avail)
        self.tt["a"] = ToolTip(self.a_entry, msg.EX_TT_AVAIL, "info")
        self.a_entry.pack(fill=tk.X, expand=1)
        a_frame.pack(fill=tk.X)

        self._navigation()

        price.trace("w", lambda n, e, m, var=price: self._priceCheck(var))
        weight.trace("w", lambda n, e, m, var=weight: self._weightCheck(var))
        avail.trace("w", lambda n, e, m, var=avail: self._availCheck(var))

        return True

    def _priceCheck(self, var):
        """ Trace price variable - check for validity """

        price = var.get()
        try:
            price = price.replace(",", ".")
            price = float(price)
            if price < 0.01:
                raise ValueError
            self.p_entry.config(style="TEntry")
            self.tt["p"].update(
                msg.EX_TT_PRICE_OKAY,
                "okay"
            )
        except ValueError:
            self.p_entry.config(style="invalid.TEntry")
            self.tt["p"].update(
                msg.EX_TT_PRICE_INVALID,
                "error"
            )

    def _weightCheck(self, var):
        """ Trace weight variable - check for validity """
        weight = var.get()
        try:
            weight = int(weight)
            if weight < 1:
                raise ValueError
            self.w_entry.config(style="TEntry")
            self.tt["w"].update(
                msg.EX_TT_WEIGHT_OKAY,
                "okay"
            )
        except ValueError:
            self.w_entry.config(style="invalid.TEntry")
            self.tt["w"].update(
                msg.EX_TT_WEIGHT_INVALID,
                "error"
            )

    def _availCheck(self, var):
        """ Trace availability variable - check for validity"""
        avail = var.get()
        try:
            avail = int(avail)
            if not -6 <= avail <= 6:
                raise ValueError
            self.a_entry.config(style="TEntry")
            self.tt["a"].update(
                msg.EX_TT_AVAIL_OKAY,
                "okay"
            )

        except ValueError:
            self.a_entry.config(style="invalid.TEntry")
            self.tt["a"].update(
                msg.EX_TT_AVAIL,
                "error"
            )

    def _addDamage(self):
        """ Screen defining damage values for an item """

        # these types can have a damage setting
        damage_types = [
            msg.EX_IT_ARMOR,
            msg.EX_IT_NATURAL,
            msg.EX_IT_CLUB,
            msg.EX_IT_BLADE,
            msg.EX_IT_STAFF,
            msg.EX_IT_OTHER_MELEE,
            msg.EX_IT_REVOLVER,
            msg.EX_IT_PISTOL,
            msg.EX_IT_RIFLE,
            msg.EX_IT_SHOT_GUN,
            msg.EX_IT_RIFLE_SA,
            msg.EX_IT_SHOT_GUN_SA,
            msg.EX_IT_AUTOMATIC_WEAPON,
            msg.EX_IT_BLASTER,
            msg.EX_IT_BLASTER_SA,
            msg.EX_IT_TOOLS,
            msg.EX_IT_IMPLANT_PART
        ]

        # these need a caliber
        caliber_types = [
            msg.EX_IT_REVOLVER,
            msg.EX_IT_PISTOL,
            msg.EX_IT_RIFLE,
            msg.EX_IT_SHOT_GUN,
            msg.EX_IT_RIFLE_SA,
            msg.EX_IT_SHOT_GUN_SA,
            msg.EX_IT_AUTOMATIC_WEAPON,
            msg.EX_IT_BLASTER,
            msg.EX_IT_BLASTER_SA,
            msg.EX_IT_CLIP,
            msg.EX_IT_AMMO,
        ]

        # these need an ammo tag
        ammo_types = [
            msg.EX_IT_REVOLVER,
            msg.EX_IT_PISTOL,
            msg.EX_IT_RIFLE,
            msg.EX_IT_SHOT_GUN,
            msg.EX_IT_RIFLE_SA,
            msg.EX_IT_SHOT_GUN_SA,
            msg.EX_IT_AUTOMATIC_WEAPON,
            msg.EX_IT_BLASTER,
            msg.EX_IT_BLASTER_SA,
        ]

        # these should have a chamber value
        chamber_types = [
            msg.EX_IT_REVOLVER,
            msg.EX_IT_RIFLE_SA,
            msg.EX_IT_SHOT_GUN_SA,
            msg.EX_IT_BLASTER_SA,
        ]

        # break for items that don't have damage values
        selected_type = self.data["type"].get()
        if selected_type not in damage_types + caliber_types:
            return False

        self._clear()
        self._showName()

        if self.data.get("damage"):
            damage = self.data["damage"]
        else:
            self.data["damage"] = damage = tk.StringVar()

        damage.trace("w", lambda n, e, m, var=damage: self._checkDamage(var))
        label = msg.EX_DAMAGE
        if selected_type == msg.EX_IT_ARMOR:
            label = msg.EX_DEFENSE
        d_frame = tk.LabelFrame(self, text=label)
        self.d_entry = tk.Entry(d_frame, textvariable=damage)
        self.d_entry.pack(fill=tk.X, expand=1)
        self.tt["d"] = ToolTip(
            self.d_entry,
            msg.EX_TT_DAMAGE,
            "info"
        )
        d_frame.pack(fill=tk.X, expand=1)

        cals = [
            ".22 long",
            ".38 short",
            ".38 Special",
            "9x19 mm",
            ".357 ParaTec",
            ".500 OMG",
            "5.56x45mm NA",
            ".223 SMI",
            "7.62x51mm NA",
            ".308FuDW",
            ".50 OMG",
            "HLK II",
            "HLK III"
        ]

        a_frame = tk.Frame(self)
        if selected_type in caliber_types:
            if self.data.get("caliber"):
                cal = self.data["caliber"]
            else:
                self.data["caliber"] = cal = tk.StringVar()

            cal_frame = tk.LabelFrame(a_frame, text=msg.EX_CALIBER)
            cal_box = tk.Combobox(cal_frame, textvariable=cal, values=cals)
            cal_box.pack(fill=tk.X, expand=1)
            cal_frame.pack(side=tk.LEFT, fill=tk.X, expand=1)

            if selected_type in ammo_types:
                if self.data.get("ammo"):
                    ammo = self.data["ammo"]
                else:
                    self.data["ammo"] = ammo = tk.StringVar()
                    ammo.set("1")

                if selected_type in chamber_types:
                    chamber_frame = tk.LabelFrame(a_frame, text=msg.EX_CHAMBERS)
                    chamber_sel = tk.Spinbox(
                        chamber_frame,
                        from_=1,
                        to=100,
                        width=4,
                        textvariable=ammo
                    )
                    chamber_sel.pack(fill=tk.X, expand=1)
                    chamber_frame.pack(side=tk.LEFT)
        a_frame.pack()

        self._navigation()
        return True

    def _checkDamage(self, var):
        """ Trace the damage variable - check for validity """

        damage = var.get()
        if "e" in damage:
            damage = damage.replace("e", "E")
            var.set(damage)

        try:
            if "/" not in damage:
                raise ValueError

            damage = damage.split("/")
            if len(damage) >= 2:
                s = int(damage[0])
                d = int(damage[1])

                if not -7 <= d <= 7:
                    raise ValueError
            if len(damage) == 3:
                e = damage[2]
                if e != "E":
                    raise ValueError
            if len(damage) > 3:
                raise ValueError

            self.d_entry.config(style="TEntry")
            self.tt["d"].update(
                msg.EX_TT_DAMAGE_OKAY,
                "okay"
            )
        except ValueError:
            self.d_entry.config(style="invalid.TEntry")
            self.tt["d"].update(
                msg.EX_TT_DAMAGE,
                "error"
            )

    def _addContainer(self):
        """ screen for setting container properties of the item """

        containers = [
            msg.EX_IT_CLOTHING,
            msg.EX_IT_HARNESS,
            msg.EX_IT_ARMOR,
            msg.EX_IT_BAG,
            msg.EX_IT_BOX,
            msg.EX_IT_CONTAINER,
            msg.EX_IT_CLIP,
            msg.EX_IT_TOOLS,
            msg.EX_IT_PROSTHESIS,
            msg.EX_IT_IMPLANT_PART
        ]

        self._clear()
        self._showName()

        # break for items that don't have containers
        selected_type = self.data["type"].get()
        if selected_type not in containers:
            return False
        
        if self.data.get("container"):
            use = self.data["container"]
        else:
            self.data["container"] = use = tk.IntVar()
            use.set(1)
        
        if self.data.get("container_name"):
            name = self.data["container_name"]
        else:
            self.data["container_name"] = name = tk.StringVar()
            
        if self.data.get("container_size"):
            size = self.data["container_size"]
        else:
            self.data["container_size"] = size = tk.StringVar()
            size.set("0")

        if self.data.get("container_limit"):
            limit = self.data["container_limit"]
        else:
            self.data["container_limit"] = limit = tk.StringVar()
            limit.set("0")

        use_container = tk.Checkbutton(
            self,
            text=msg.EX_USE_CONTAINER,
            onvalue=1,
            offvalue=0,
            variable=use
        )
        use_container.pack(fill=tk.X)
        name_frame = tk.LabelFrame(self, text=msg.EX_DISPLAY_NAME)
        self.n_entry = tk.Entry(name_frame, textvariable=name)
        self.n_entry.pack(fill=tk.X, expand=1)
        self.tt["n"] = ToolTip(self.n_entry, msg.EX_TT_CONT_NO_NAME, "info")

        name_frame.pack(fill=tk.X, expand=1)
        frame = tk.Frame(self)
        size_frame = tk.LabelFrame(frame, text=msg.EX_CONTAINER_SIZE)
        self.s_entry = tk.Entry(size_frame, textvariable=size)
        self.s_entry.pack(fill=tk.X, expand=1)
        self.tt["s"] = ToolTip(self.s_entry, msg.EX_TT_CONT_SIZE, "info")

        size_frame.grid(row=0, column=0, sticky=tk.NSEW)
        limit_frame = tk.LabelFrame(frame, text=msg.EX_CONTAINER_LIMIT)
        self.l_entry = tk.Entry(limit_frame, textvariable=limit)
        self.l_entry.pack(fill=tk.X, expand=1)
        self.tt["l"] = ToolTip(self.l_entry, msg.EX_TT_CONT_LIMIT, "info")
        limit_frame.grid(row=0, column=1, sticky=tk.NSEW)
        frame.pack(fill=tk.X, expand=1)

        limit.trace("w", lambda n, e, m: self._checkContainer())
        size.trace("w", lambda n, e, m: self._checkContainer())
        name.trace("w", lambda n, e, m: self._checkContainer())
        self._navigation()
        return True

    def _checkContainer(self):
        """ Trace container variables - validate values"""

        try:
            limit = self.data["container_limit"].get()
            limit = int(limit)
            if limit < 0:
                raise ValueError
            self.l_entry.config(style="TEntry")
            self.tt["l"].update(
                msg.EX_TT_CONT_LIMIT,
                "okay"
            )

        except ValueError:
            self.l_entry.config(style="invalid.TEntry")
            self.tt["l"].update(
                msg.EX_TT_CONT_ERROR,
                "error"
            )

        try:
            size = self.data["container_size"].get()
            size = int(size)
            if size < 0:
                raise ValueError
            self.s_entry.config(style="TEntry")
            self.tt["s"].update(
                msg.EX_TT_CONT_SIZE,
                "okay"
            )
        except ValueError:
            self.s_entry.config(style="invalid.TEntry")
            self.tt["s"].update(
                msg.EX_TT_CONT_ERROR,
                "error"
            )

        name = self.data["container_name"].get()
        invalid = re.findall("[\"\'&§<>]", name)
        if len(invalid) > 0:
            self.tt["n"].update(
                msg.EX_TT_CONT_NAME_INVALID,
                "error"
            )
            self.n_entry.config(style="invalid.TEntry")
        elif len(name) == 0:
            self.tt["n"].update(
                msg.EX_TT_CONT_NO_NAME,
                "okay"
            )
            self.n_entry.config(style="TEntry")

        else:
            self.tt["n"].update(
                msg.EX_TT_CONT_NAME_OKAY,
                "okay"
            )
            self.n_entry.config(style="TEntry")

    def _addOptions(self):
        """ Screen for adding additonal item options and packs. """

        self._clear()
        self._showName()

        if self.data.get("min_q"):
            min_q = self.data["min_q"]
        else:
            self.data["min_q"] = min_q = tk.IntVar()
            min_q.set(3)
        
        if self.data.get("max_q"):
            max_q = self.data["max_q"]
        else:
            self.data["max_q"] = max_q = tk.IntVar()
            max_q.set(9)

        q_frame = tk.Frame(self)
        ToolTip(q_frame, msg.EX_TT_QUALITY, "info")
        q_frame.columnconfigure(0, weight=1)
        q_frame.columnconfigure(1, weight=1)
        min_q_frame = tk.LabelFrame(q_frame, text=msg.EX_MIN_QUALITY)
        self.min_q_label = tk.Label(min_q_frame, text=" ")
        self.min_q_label.pack()
        self.min_q = tk.Scale(
            min_q_frame,
            from_=3,
            to=9,
            variable=min_q,
            command=lambda v, var=min_q: self._updateQuality(var)
        )
        self.min_q.pack(fill=tk.X)
        min_q_frame.grid(row=0, column=0, sticky=tk.NSEW)

        max_q_frame = tk.LabelFrame(q_frame, text=msg.EX_MAX_QUALITY)
        self.max_q_label = tk.Label(max_q_frame, text=" ")
        self.max_q_label.pack()
        self.max_q = tk.Scale(
            max_q_frame,
            from_=3,
            to=9,
            variable=max_q,
            command=lambda v, var=max_q: self._updateQuality(var)
        )
        self.max_q.pack(fill=tk.X)
        max_q_frame.grid(row=0, column=1, sticky=tk.NSEW)
        q_frame.pack(fill=tk.X)

        if self.data.get("options"):
            options = self.data["options"]
        else:
            self.data["options"] = options = {
                "color": [tk.IntVar(), tk.StringVar()],
                "size": [tk.IntVar(), tk.StringVar()],
                "material": [tk.IntVar(), tk.StringVar()],
                "variant": [tk.IntVar(), tk.StringVar()],
            }

            options["color"][0].set(0)
            options["size"][0].set(0)
            options["material"][0].set(0)
            options["variant"][0].set(0)

        o_frame = tk.LabelFrame(self, text=msg.EX_OPTIONS)
        l = [
            ("color", msg.IE_OPTION_COLOR),
            ("material", msg.IE_OPTION_MATERIAL),
            ("size", msg.IE_OPTION_SIZE),
            ("variant", msg.IE_OPTION_VARIANT),
        ]
        o_frame.columnconfigure(1, weight=100)
        for i, o in enumerate(l):
            cb = tk.Checkbutton(
                o_frame,
                text=o[1],
                onvalue=1,
                offvalue=0,
                variable=options[o[0]][0]
            )
            cb.grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(
                o_frame,
                textvariable=options[o[0]][1]
            )
            self.tt[o[0]] = ToolTip(entry, msg.EX_TT_OPTION, "info")
            options[o[0]][1].trace(
                "w",
                lambda n, e, w, name=o[0], var=options[o[0]][1], widget=entry:
                    self._checkOptions(name, var, widget)
            )
            entry.grid(row=i, column=1, sticky=tk.NSEW)

        o_frame.pack(fill=tk.X, expand=1)

        if self.data.get("packs"):
            packs = self.data["packs"]
        else:
            self.data["packs"] = packs = ""

        p_frame = tk.LabelFrame(self, text=msg.EX_PACK_UNITS)
        p_text = tk.Text(
            p_frame,
            width=10,
            height=3
        )
        p_text.insert("0.0", packs)
        p_text.bind("<KeyRelease>", self._updatePacks)
        p_text.pack(fill=tk.BOTH, expand=1)
        self.tt["p"] = ToolTip(p_text, msg.EX_TT_PACKS, "info")

        p_frame.pack(fill=tk.X)
        self._navigation()
        self._updateQuality()
        return True

    def _checkOptions(self, name, var, widget):
        """ Trace option variables and validate the values """

        value = var.get()

        invalid = re.findall("[\"\'&§<>]", value)
        count = len(value.split(","))

        if len(invalid) > 0:
            widget.config(style="invalid.TEntry")
            self.tt[name].update(
                msg.EX_TT_OPT_INVALID,
                "error"
            )
        else:
            widget.config(style="TEntry")

        if len(value) == 0:
            self.tt[name].update(
                msg.EX_TT_OPT_EMPTY,
                "okay"
            )
        elif count == 1:
            self.tt[name].update(
                msg.EX_TT_OPT_SINGLE,
                "okay"
            )
        elif count > 1:
            info = msg.EX_TT_OPT_OKAY.format(n=count)
            self.tt[name].update(info, "okay")

    def _updatePacks(self, event):
        """ handles changes in the packs field and validate content """

        self.data["packs"] = packs = event.widget.get("0.0", tk.END)

        l = packs.split("\n")
        l = l[0:-1]
        for line in l:
            if not line and len(l) == 1:
                self.tt["p"].update(
                    msg.EX_TT_PACKS_NONE,
                    "okay"
                )
                return
            if ":" in line:
                count, name = line.split(":")
                invalid = re.findall("[\"\'&§<>]", name)
                if len(invalid) > 0:
                    self.tt["p"].update(
                        msg.EX_TT_PACKS,
                        "error"
                    )
                    return
                try:
                    count = int(count)
                    if count < 1: raise ValueError
                except ValueError:
                    self.tt["p"].update(
                        msg.EX_TT_PACKS,
                        "error"
                    )
                    return
            else:
                self.tt["p"].update(
                    msg.EX_TT_PACKS,
                    "error"
                )
                return

        if len(l) == 1:
            self.tt["p"].update(
                msg.EX_TT_PACKS_SINGLE,
                "okay"
            )
        else:
            self.tt["p"].update(
                msg.EX_TT_PACKS_MULTI.format(n=len(l)),
                "okay"
            )

    def _updateQuality(self, var=None):
        """ Updating the quality variables and info widgets """

        min_q = self.data["min_q"]
        max_q = self.data["max_q"]

        if var is min_q and min_q.get() > max_q.get():
            max_q.set(min_q.get())

        if var is max_q and max_q.get() < min_q.get():
            min_q.set(max_q.get())

        qualities = {
            3: msg.IE_QUALITY_3,
            4: msg.IE_QUALITY_4,
            5: msg.IE_QUALITY_5,
            6: msg.IE_QUALITY_6,
            7: msg.IE_QUALITY_7,
            8: msg.IE_QUALITY_8,
            9: msg.IE_QUALITY_9,
        }

        self.min_q_label.config(text=qualities[min_q.get()])
        self.max_q_label.config(text=qualities[max_q.get()])

    def _addDescription(self):
        """ Screen for adding a item description. """

        self._clear()
        self._showName()

        if self.data.get("description"):
            desc = self.data["description"]
        else:
            self.data["description"] = desc = ""

        t_frame = tk.LabelFrame(self, text=msg.EX_DESCRIPTION)
        textfield = tk.Text(
            t_frame,
            width=20,
            height=8,
            wrap=tk.WORD,

        )
        textfield.insert("0.0", desc)
        textfield.bind("<KeyRelease>", self._updateDescription)
        textfield.pack(fill=tk.BOTH, expand=1)
        t_frame.pack(fill=tk.BOTH, expand=1)

        self._navigation()

        return True

    def _updateDescription(self, event):
        """ Handles changes in the item description and stores it """
        self.data["description"] = event.widget.get("0.0", tk.END)

    def _addParent(self):
        """Screen for setting the items parent """

        self._clear()
        self._showName()

        if self.data.get("parent"):
            menu = self.data["parent"]
        else:
            self.data["parent"] = menu = tk.StringVar()

        selector_list_frame = tk.LabelFrame(self, text=msg.EX_MENU_POS)
        self.selector_list = tk.Treeview(
            selector_list_frame,
            selectmode=tk.BROWSE,
            show="tree",
            height=8
        )
        self.selector_list.bind("<<TreeviewSelect>>", self._parentSelect)
        self.selector_scroll = tk.Scrollbar(
            selector_list_frame,
            orient=tk.VERTICAL,
            command=self.selector_list.yview
        )
        self.selector_list.config(yscrollcommand=self.selector_scroll.set)
        self.selector_scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=1)
        self.selector_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        selector_list_frame.pack(
            fill=tk.BOTH,
            expand=1,
            anchor=tk.W
        )
        self.selector_list.focus()

        groups = self.app.itemlist.getGroups()

        self.foldericon = ImageTk.PhotoImage(file="img/folder.png")

        nodes = {}
        active = None
        for group in groups:
            group_id = group.get("id", "0")
            if self.data["parent"].get() == group_id:
                active = group_id
            parent_id = group.get("parent", "")
            parent = nodes.get(parent_id, "")
            nodes[group_id] = self.selector_list.insert(
                parent,
                1000,
                image=self.foldericon,
                text=group.get("name", "...")
            )

        if active:
            self.selector_list.see(nodes[active])
            self.selector_list.selection_set(nodes[active])

        self._navigation()
        return True

    def _parentSelect(self, event):
        """ Handles changes it parent selection"""

        sel = self.selector_list.selection()
        if sel:
            name = self.selector_list.item(sel)["text"]
            groups = self.app.itemlist.getGroups()
            for group in groups:
                if group.get("name") == name:
                    id = group.get("id")
                    self.data["parent"].set(id)
        else:
            self.data["parent"].set("")

    def _finalizeItem(self):
        errors = self._checkAll()
        if errors:
            errors = "\n".join(errors)
            tkmb.showerror(msg.EX_ITEM_NOT_SAVED, errors, parent=self)
            self.page = 7
            self._lastPage()
            return

        name = self.data["name"].get()
        weight = self.data["weight"].get()
        price = self.data["price"].get()
        avail = self.data["avail"].get()
        parent = self.data["parent"].get()

        item_type = self._itemtypes()[self.data["type"].get()]
        self.item.set("name", name)
        self.item.set("weight", weight)
        self.item.set("price", price)
        self.item.set("avail", avail)
        self.item.set("type", item_type)
        self.item.set("parent", parent)

        valid_q = ["3", "4", "5", "6", "7", "8", "9"]
        if self.data["min_q"] in valid_q and self.data["max_q"] in valid_q:
            qual_range = self.data["min_q"] + " " + self.data["max_q"]
            self.item.set("quality", qual_range)

        self._setDamage()

        self._setContainer()

        self._setOptions()

        self._setPacks()

        desc = self.item.get("description")
        if desc is not None:
            desc.text = self.data["description"]
        else:
            desc = et.SubElement(self.item, "description")
            desc.text = self.data["description"]

        items = self.app.module.expansion.find(".//items")
        if self.item in items:
            items.remove(self.item)
        items.append(self.item)

        self.app.module.updateItems()
        self.close()

    def _setDamage(self):
        if self.data.get("damage"):
            damage_tag = self.item.find("damage")
            if damage_tag is not None:
                damage_tag.set("value", self.data["damage"].get())
            else:
                et.SubElement(
                    self.item,
                    "damage",
                    {"value": self.data["damage"].get()}
                )

        if self.data.get("ammo"):
            ammo_tag = self.item.find("ammo")
            chambers = self.data["ammo"].get()
            if ammo_tag is not None:
                ammo_tag.set("chambers", chambers)
            else:
                et.SubElement(
                    self.item,
                    "ammo",
                    {"chambers": chambers}
                )

        if self.data.get("caliber"):
            cal_name = config.ItemTypes.OPTION_CALIBER

            cal_tag = self.item.find("option[@name='"+cal_name+"']")
            if cal_tag is not None:
                cal_tag.set("values", self.data["caliber"].get())
            else:
                et.SubElement(
                    self.item,
                    "option",
                    {"name": cal_name,
                     "values": self.data["caliber"].get()}
                )

    def _setContainer(self):
        if self.data.get("container"):
            if self.data["container"].get() == 1:
                container_tag = self.item.find("container")
                c_name = self.data["container_name"].get()
                if not c_name:
                    c_name = self.data["name"].get()
                limit = self.data["container_limit"].get()
                size = self.data["container_size"].get()

                if container_tag is not None:
                    container_tag.set("name", c_name)
                    container_tag.set("size", size)
                    container_tag.set("limit", limit)
                else:
                    container_tag = et.SubElement(
                        self.item,
                        "container",
                        {"name": c_name,
                         "size": size,
                         "limit": limit}
                    )

                if limit == "0":
                    del container_tag.attrib["limit"]
                if size == "0":
                    del container_tag.attrib["size"]

            else:
                container_tag = self.item.find("container")
                if container_tag is not None:
                    self.item.remove(container_tag)

    def _setOptions(self):
        it = config.ItemTypes
        options = [
            it.OPTION_COLOR,
            it.OPTION_MATERIAL,
            it.OPTION_SIZE,
            it.OPTION_VARIANT
        ]
        for option in options:
            use = self.data["options"][option][0].get()
            values = self.data["options"][option][1].get()

            option_tag = self.item.find("option[@name='"+option+"']")
            if use:
                if option_tag is None:
                    option_tag = et.SubElement(
                        self.item,
                        "option",
                        {"name": option}
                    )

                if values and "," in values:
                    values = values.split(",")
                    for value in values:
                        value = value.strip()
                    values = ",".join(values)
                    option_tag.set("values", values)
                elif len(values) > 0:
                    option_tag.set("values", values)
                else:
                    if option_tag.get("values"):
                        option_tag.pop("values")
            else:
                if option_tag is not None:
                    self.item.remove(option_tag)

    def _setPacks(self):
        packs = self.item.findall("pack")
        for pack in packs:
            self.item.remove(pack)

        if len(self.data["packs"]) > 0:
            packs = self.data["packs"].split("\n")
            for pack in packs:
                if ":" not in pack: continue
                q, name = pack.split(":")
                name = name.strip()
                name = name + " (" + q + ")"
                et.SubElement(
                    self.item,
                    "pack",
                    {"name": name,
                     "quantity": q}
                )

    def _checkAll(self):
        # basic data:

        errors = []

        name = self.data["name"].get()
        invalid = re.findall("[\"\'&§<>]", name)
        if len(name) == 0:
            errors.append(msg.EX_ERROR_NAME_EMPTY)
        if len(invalid) > 0:
            errors.append(msg.EX_ERROR_NAME_INVALID)

        weight = self.data["weight"].get()
        try:
            weight = int(weight)
            if weight < 0: 
                raise ValueError
        except ValueError:
            errors.append(msg.EX_ERROR_WEIGHT)

        price = self.data["price"].get()
        try: 
            price = price.replace(",", ".")
            price = float(price)
            if price < 0: 
                raise ValueError
        except ValueError:
            errors.append(msg.EX_ERROR_PRICE)

        avail = self.data["avail"].get()
        try:
            avail = int(avail)
            if not -6 <= avail < 6:
                raise ValueError
        except ValueError:
            errors.append(msg.EX_ERROR_AVAIL)

        damage = self.data.get("damage")
        if damage:
            damage = damage.get()
            try:
                if "/" not in damage:
                    raise ValueError

                damage = damage.split("/")
                if len(damage) >= 2:
                    s = int(damage[0])
                    d = int(damage[1])

                    if not -7 <= d <= 7:
                        raise ValueError
                if len(damage) == 3:
                    e = damage[2]
                    if e.lower() != "e":
                        raise ValueError
                if len(damage) > 3:
                    raise ValueError

            except ValueError:
                errors.append(msg.EX_ERROR_DAMAGE)

            ammo = self.data.get("ammo")
            if ammo:
                ammo = ammo.get()
                try:
                    ammo = int(ammo)
                    if ammo < 1:
                        raise ValueError
                except ValueError:
                    errors.append(msg.EX_ERROR_CHAMBERS)

        container = self.data.get("container")
        if container:
            use = container.get()
            if use:
                size = self.data["container_size"].get()
                limit = self.data["container_limit"].get()
                try:
                    size = int(size)
                    limit = int(limit)
                    if size < 0: raise ValueError
                    if limit < 0: raise ValueError
                except ValueError:
                    errors.append(msg.EX_ERROR_CONTAINER)

        it = config.ItemTypes()
        options = [
            it.OPTION_VARIANT,
            it.OPTION_MATERIAL,
            it.OPTION_SIZE,
            it.OPTION_SIZE
        ]
        for option in options:
            values = self.data["options"][option][1].get()
            invalid = re.findall("[\"\'&§<>]", values)
            if len(invalid) > 0:
                if msg.EX_ERROR_INVALID_OPTION not in errors:
                    errors.append(msg.EX_ERROR_INVALID_OPTION)

        desc = self.data["description"]
        invalid = re.findall("[&§<>]", desc)
        if len(invalid) > 0:
            errors.append(msg.EX_ERROR_INVALID_DESC)

        parent = self.data["parent"].get()
        print(parent)
        if parent == "":
            errors.append(msg.EX_ERROR_NO_PARENT)

        return errors

    @staticmethod
    def _itemtypes():
        it = config.ItemTypes()
        types = {
            msg.EX_IT_CLOTHING: it.CLOTHING,
            msg.EX_IT_HARNESS: it.HARNESS,
            msg.EX_IT_ARMOR: it.ARMOR,
            msg.EX_IT_BAG: it.BAG,
            msg.EX_IT_BOX: it.BOX,
            msg.EX_IT_CONTAINER: it.CONTAINER,
            msg.EX_IT_NATURAL: it.NATURAL,
            msg.EX_IT_CLUB: it.CLUB,
            msg.EX_IT_BLADE: it.BLADE,
            msg.EX_IT_STAFF: it.STAFF ,
            msg.EX_IT_OTHER_MELEE: it.OTHER_MELEE,
            msg.EX_IT_REVOLVER: it.REVOLVER,
            msg.EX_IT_PISTOL: it.PISTOL,
            msg.EX_IT_RIFLE: it.RIFLE,
            msg.EX_IT_SHOT_GUN: it.SHOT_GUN,
            msg.EX_IT_RIFLE_SA: it.RIFLE_SA,
            msg.EX_IT_SHOT_GUN_SA: it.SHOT_GUN_SA,
            msg.EX_IT_AUTOMATIC_WEAPON: it.AUTOMATIC_WEAPON,
            msg.EX_IT_BLASTER: it.BLASTER,
            msg.EX_IT_BLASTER_SA: it.BLASTER_SA,
            msg.EX_IT_CLIP: it.CLIP,
            msg.EX_IT_AMMO: it.AMMO,
            msg.EX_IT_TOOLS: it.TOOLS,
            msg.EX_IT_MONEY: it.MONEY,
            msg.EX_IT_SERVICE: it.SERVICE,
            msg.EX_IT_FOOD: it.FOOD,
            msg.EX_IT_DRUG: it.DRUG,
            msg.EX_IT_GENERIC: it.GENERIC,
            msg.EX_IT_IMPLANT: it.IMPLANT,
            msg.EX_IT_PROSTHESIS: it.PROSTHESIS,
            msg.EX_IT_IMPLANT_PART: it.IMPLANT_PART
        }

        return types

    def _navigation(self):

        self.c_button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._nextPage
        )
        self.c_button.pack(fill=tk.X, expand=1)
        self.b_button = tk.Button(
            self,
            text=msg.EX_BACK,
            command=self._lastPage
        )
        if self.page != 1:
            self.b_button.pack(fill=tk.X, expand=1)

    def _nextPage(self):
        self.page += 1
        try:
            pages = {
                1: self._addName,
                2: self._addData,
                3: self._addDamage,
                4: self._addContainer,
                5: self._addOptions,
                6: self._addDescription,
                7: self._addParent,
                8: self._finalizeItem,

            }

            switch = pages[self.page]()

            if not switch:
                self._nextPage()

        except KeyError:
            self.close()

    def _lastPage(self):
        self.page -= 1
        try:
            pages = {
                1: self._addName,
                2: self._addData,
                3: self._addDamage,
                4: self._addContainer,
                5: self._addOptions,
                6: self._addDescription,
                7: self._addParent,
            }

            switch = pages[self.page]()

            if not switch:
                self._lastPage()

        except KeyError:
            self.close()

    def close(self):
        self.app.open_windows["skill"] = 0
        self.destroy()


class SkillEditor(tk.Toplevel):
    """ The skill editor is used to create or edit skills in an expansion
    
    Args: 
        master(tk.Widget): tkinter master widget
        app(Application): the main application instance
        skill(et.Element<skill>): the skill to edit (None is new)
    """

    def __init__(
        self,
        master=None,
        app=None,
        skill=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.app = app
        self.style = app.style

        self.minsize(200, 100)

        self.loaded_skills = None
        self.data = {}

        self.skill = skill
        if self.skill is None:
            self.skill = et.Element("skill")
            self.loaded_skills = self._list()
            self._newSkill()
        else:
            self._editSkill()

    def _list(self):
        """ get a list of all used skill names """

        cur = [s[0] for s in self.app.skills.getList()]
        exp = self.app.module.expansion.findall(".//skill")
        name = self.skill.get("name")
        exp = [s.get("name") for s in exp if s.get("name") != name]
        return cur + exp

    def _clear(self):
        """ clears the window for the next step """
        widgets = self.winfo_children()
        for widget in widgets:
            widget.destroy()

    def _newSkill(self):
        """ first step, give it a name ..."""

        self._clear()

        frame = tk.LabelFrame(self, text=msg.NAME)

        if self.data.get("name"):
            var = self.data.get("name")
        else:
            self.data["name"] = var = tk.StringVar()
        var.trace("w", lambda n, e, m, var=var: self._checkName(var))

        # set name if the skill already has a name
        if self.skill.get("name"):
            var.set(self.skill.get("name"))

        entry = tk.Entry(frame, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        frame.pack(fill=tk.X)

        self._selectParent()

        tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._finalizeSkill
        ).pack(fill=tk.X)

    def _checkName(self, var):
        """ disables 'continue button' if name exists """

        cur_name = var.get()
        if cur_name in self.loaded_skills:
            pass
        else:
            pass

    def _editSkill(self):
        self.loaded_skills = self._list()

        frame = tk.LabelFrame(self, text=msg.NAME)

        if self.data.get("name"):
            var = self.data.get("name")
        else:
            self.data["name"] = var = tk.StringVar()
        var.trace("w", lambda n, e, m, var=var: self._checkName(var))

        # set name if the skill already has a name
        if self.skill.get("name"):
            var.set(self.skill.get("name"))

        entry = tk.Entry(frame, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        frame.pack(fill=tk.X)

        self.data["parent"] = parent_id = self.skill.get("parent")

        self.parent = self.app.skills.getSkillById(parent_id)

        if self.parent is None:
            exp = self.app.module.expansion
            self.parent = exp.find(".//skill[@id='" + parent_id + "']")

        self.data["parent_name"] = self.parent.get("name")

        self.data["spec"] = int(self.skill.get("spec"))

        if self.data.get("id"):
            id_var = self.data["id"]
        else:
            self.data["id"] = id_var = tk.StringVar()
            id_var.set(self.skill.get("id"))

        self.data["type"] = self.skill.get("type")

        self.frame = tk.Frame(self)
        self.frame = self._showSkillData(self.frame, edit=True)
        self.frame.pack(fill=tk.BOTH, expand=1)

    def _editParent(self, event):
        self.frame.destroy()
        self._selectParent()
        tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._finalizeSkill
        ).pack(fill=tk.X)

    def _selectParent(self):

        super_frame = tk.LabelFrame(self, text=msg.EX_SUPER_SKILL)
        if self.data.get("super_search"):
            var = self.data.get("super_search")
        else:
            self.data["super_search"] = var = tk.StringVar()

        # set parent, if it is an edit
        if self.skill.get("parent"):
            p_id = self.skill.get("parent")
            parent = self.app.skills.getSkillById(p_id)
            if parent is None:
                search = ".//skill[@id='"+p_id+"']"
                parent = self.app.module.expansion.find(search)
            if parent is not None:
                var.set(parent.get("name"))

        var.trace("w", lambda n, e, m, var=var: self._searchSuper(var))

        entry = tk.Entry(super_frame, textvariable=var)
        entry.pack(fill=tk.X, expand=1)
        list_frame = tk.Frame(super_frame)
        self.skill_list = tk.Listbox(list_frame)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=self.skill_list.yview)
        self.skill_list.config(yscrollcommand=scroll.set)
        self.skill_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack(fill=tk.BOTH, expand=1)

        super_frame.pack(fill=tk.BOTH)

        # fill the list

        l = self._getSkills()
        self.skill_list.insert(0, *l)

        # select parent, if it is an edit
        if var.get() in l:
            index = l.index(var.get())
            self.skill_list.select_set(index)
        if "    "+var.get() in l:
            index = l.index("    "+var.get())
            self.skill_list.select_set(index)

    def _getSkills(self):

        def getExpSkills(self):
            exp_skills = self.app.module.expansion.findall(".//skill")
            result = []
            for skill in exp_skills:
                name = skill.get("name")
                spec = skill.get("spec")
                if spec == "3":
                    continue
                id = int(skill.get("id"))
                result.append((name, spec, id, 0))
            return result

        skills = self.app.skills.getList(maxspec=2)
        skills += getExpSkills(self)
        skills = sorted(skills, key=lambda x: x[2])

        result = [s[0] if s[1] == 1 else "    "+s[0] for s in skills]
        return result

    def _searchSuper(self, var):
        """ filter list by entry field """

        # for some reason an error is thrown on going back to
        # the parent selection so this makes sure it doesn't ...
        try:
            search = var.get().lower()
            l = [s for s in self.loaded_skills if search in s.lower()]
            self.skill_list.delete(0, tk.END)
            self.skill_list.insert(0, *l)
        except tk.TclError:
            pass

    def _finalizeSkill(self):
        """ last step, skill metadata and display ... """

        selected = self.skill_list.curselection()
        if len(selected) != 1:
            tkmb.showerror(msg.ERROR, msg.EX_NO_SUPER_SKILL, parent=self)
            return

        # there we go ...
        else:
            super_name = self.skill_list.get(selected[0]).strip()
            self.parent = self.app.skills.getSkill(super_name)
            if self.parent is None:
                exp = self.app.module.expansion
                self.parent = exp.find(".//skill[@name='" + super_name + "']")
            self.data["parent"] = parent_id = int(self.parent.get("id"))
            self.data["parent_name"] = self.parent.get("name")
            self.skill.set("parent", str(parent_id))
            new_id = parent_id

            exists = True
            self.data["spec"] = spec = int(self.parent.get("spec")) + 1
            factor = 1
            if spec == 2:
                factor = 100
            while exists is not None:
                new_id += factor
                exists = self.app.skills.getSkillById(new_id)

            if self.data.get("id"):
                id_var = self.data["id"]
            else:
                self.data["id"] = id_var = tk.StringVar()
            id_var.set(str(new_id))

            self.data["type"] = self.parent.get("type")

            self._displaySkill()

    def _displaySkill(self):
        self._clear()

        frame = tk.LabelFrame(self, text=msg.EX_NEW_SKILL)
        name = self.data["name"].get()
        self.skill.set("name", name)
        tk.Label(
            frame,
            text=name,
            font="Arial 12 bold"
        ).pack(anchor=tk.CENTER)

        frame = self._showSkillData(frame)

        frame.pack(fill=tk.BOTH)

        tk.Button(
            self,
            text=msg.EX_FINISH,
            command=self._addSkill
        ).pack(fill=tk.X)
        tk.Button(
            self,
            text=msg.EX_BACK,
            command=self._newSkill
        ).pack(fill=tk.X)
        tk.Button(
            self,
            text=msg.EX_ABORT,
            command=self.close
        ).pack(fill=tk.X)

    def _showSkillData(self, frame, edit=False):

        types = {
            "active": msg.EX_ACTIVE_SKILL,
            "passive": msg.EX_PASSIVE_SKILL,
            "lang": msg.EX_LANGUAGE_SKILL
        }
        specs = {
            2: msg.EX_SPEC2,
            3: msg.EX_SPEC3
        }

        tk.Label(
            frame,
            text=types[self.data["type"]]
        ).pack(anchor=tk.CENTER)
        parent = tk.Label(
            frame,
            text=specs[self.data["spec"]] + self.data["parent_name"]
        )

        if edit:
            edit_icon = ImageTk.PhotoImage(file="img/edit_s.png")
            parent.config(
                image=edit_icon,
                compound=tk.RIGHT
            )
            parent.bind("<Button-1>", self._editParent)
            parent.image=edit_icon
        parent.pack(anchor=tk.CENTER)

        # the id is editable but disabled ...
        id_frame = tk.Frame(frame)
        tk.Label(id_frame, text=msg.EX_ID).pack(side=tk.LEFT)
        id_entry = tk.Entry(
            id_frame,
            textvariable=self.data["id"],
            style="edit_entry",
            width="7"
        )

        id_entry.config(state=tk.DISABLED)

        def enable(event):
            event.widget.config(state=tk.NORMAL)
        id_entry.bind(
            "<Double-Button-1>",
            enable
        )

        id_entry.pack(side=tk.LEFT)
        id_frame.pack()

        return frame

    def _addSkill(self):
        """ updating the final data and writing the skill to the tree """

        self.skill.set("name", self.data["name"].get())
        self.skill.set("id", self.data["id"].get())
        self.skill.set("type", self.parent.get("type"))
        self.skill.set("spec", str(int(self.parent.get("spec")) + 1))

        skills = self.app.module.expansion.find("skills")
        if self.skill in skills:
            skills.remove(self.skill)
        skills.append(self.skill)
        self.app.module.updateSkills()

        self.close()

    def close(self):
        self.app.open_windows["skill"] = 0
        self.destroy()


class TraitEditor(tk.Toplevel):
    """ The trait editor is used to create and modify character traits
    
    Args: 
        master (tk.Widget): The parent widget
        app (Application): The main program instance
        trait (et.Element<trait>): The trait to edit - new if None
        
    """

    def __init__(
        self,
        master=None,
        app=None,
        trait=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.minsize(250, 100)

        self.app = app
        self.trait = trait

        self.name = tk.StringVar()
        self.spec = tk.StringVar()
        self.xp = tk.StringVar()
        self.group = tk.StringVar()
        self.group.set(self._traitGroupsList()[0])
        self.description = ""
        self.vars = []

        if self.trait is None:
            self.trait = et.Element("trait")

        self._displayTrait()
        self._readTrait()

    def _existingNames(self):
        """ Get a list of already existing trait names """

        traits = self.app.traits.getTraits()
        names = [t.get("name") for t in traits]
        exp_traits = self.app.module.expansion.findall(".//trait")
        names += [t.get("name") for t in exp_traits]

        if self.trait.get("name"):
            names.remove(self.trait.get("name"))

        return names

    def _displayTrait(self):
        """ Display the trait """

        def checkName(var, tt):
            """ inline check for the name run as trace on the name var."""

            name = var.get()
            invalid = re.findall("[\"\'§<>&]", name)

            if len(name) < 1:
                tt.update(msg.EX_TT_TRAIT_NAME, "error")
            elif len(invalid) > 0:
                tt.update(msg.EX_TT_NAME_INVALID, "error")
                tt.widget.config(style="invalid.TEntry")

            elif name in self._existingNames():
                tt.update(msg.EX_TT_NAME_EXISTS, "error")
                tt.widget.config(style="invalid.TEntry")
            else:
                tt.update(msg.EX_TT_NAME_OKAY, "okay")
                tt.widget.config(style="TEntry")

        def checkXP(var, tt):
            """ Inline check for the given xp value run as trace. """

            xp = var.get()
            try:
                xp = int(xp)
                if xp == 0:
                    raise ValueError
                tt.widget.config(style="TEntry")
                tt.variant = "okay"
            except ValueError:
                tt.widget.config(style="invalid.TEntry")
                tt.variant = "error"

        def checkSpec(var, tt):
            """ inline check for the specification, run as trace """

            spec = var.get()
            invalid = re.findall("[\"\'§<>&]", spec)

            if len(spec) < 1:
                tt.update(msg.EX_TT_TRAIT_SPEC_NONE, "okay")
            elif len(invalid) > 0:
                tt.update(msg.EX_TT_NAME_INVALID, "error")
                tt.widget.config(style="invalid.TEntry")
            else:
                tt.update(msg.EX_TT_TRAIT_SPEC_OKAY, "okay")
                tt.widget.config(style="TEntry")

        t_frame = tk.Frame(self)
        name_frame = tk.LabelFrame(t_frame, text=msg.NAME)
        name_entry = tk.Entry(
            name_frame,
            textvariable=self.name
        )
        tt = ToolTip(name_entry, msg.EX_TT_TRAIT_NAME, "info")
        self.name.trace(
            "w",
            lambda n, e, m, v=self.name, tt=tt:
                checkName(v, tt)
        )
        name_entry.pack(fill=tk.X, expand=1)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=1)
        xp_frame = tk.LabelFrame(t_frame, text=msg.XP)
        xp_entry = tk.Entry(
            xp_frame,
            textvariable=self.xp,
            width=3
        )
        tt = ToolTip(xp_entry, msg.EX_TT_TRAIT_XP, "info")
        self.xp.trace(
            "w",
            lambda n, e, m, v=self.xp, tt=tt:
            checkXP(v, tt)
        )

        xp_entry.pack(fill=tk.X, expand=1)
        xp_frame.pack(side=tk.LEFT, fill=tk.X, expand=1)
        t_frame.pack(fill=tk.X, expand=1)

        group_frame = tk.LabelFrame(self, text=msg.EX_TRAIT_GROUP)
        ToolTip(group_frame, msg.EX_TT_TRAIT_GROUP, "info")
        group_button = tk.OptionMenu(
            group_frame,
            self.group,
            self.group.get(),
            *self._traitGroupsList()
        )

        group_button.pack(fill=tk.X, expand=1)
        group_frame.pack(fill=tk.X, expand=1)

        spec_frame = tk.LabelFrame(self, text=msg.EX_SPECIFICATION)
        spec_entry = tk.Entry(
            spec_frame,
            textvariable=self.spec
        )
        tt = ToolTip(spec_entry, msg.EX_TT_TRAIT_SPEC, "info")
        self.spec.trace(
            "w",
            lambda n, e, m, v=self.spec, tt=tt:
            checkSpec(v, tt)
        )

        spec_entry.pack(fill=tk.X, expand=1)
        spec_frame.pack(fill=tk.X, expand=1)

        vars_frame = tk.LabelFrame(self, text=msg.EX_ADD_VARIABLES)
        var_button = tk.Button(
            vars_frame,
            text=msg.EX_VARIABLE,
            command=self._addVariable
        )
        ToolTip(var_button, msg.EX_TT_ADD_VAR)
        var_button.pack(side=tk.LEFT, fill=tk.X, expand=1)
        rank_button = tk.Button(
            vars_frame,
            text=msg.EX_RANK,
            command=self._addRank
        )
        ToolTip(var_button, msg.EX_TT_ADD_RANK)
        rank_button.pack(side=tk.LEFT, fill=tk.X, expand=1)
        vars_frame.pack(fill=tk.X, expand=1)

        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=1)

        self.desc_frame = tk.LabelFrame(self, text=msg.EX_DESCRIPTION)
        self.desc_text = tk.Text(
            self.desc_frame,
            width=10,
            height=4,
        )
        ToolTip(self.desc_text, msg.EX_TT_TRAIT_DESC)
        self.desc_text.insert("0.0", self.description)
        self.desc_text.pack(fill=tk.BOTH, expand=1)
        self.desc_text.bind(
            "<KeyRelease>",
            self._updateDescription
        )
        self.desc_frame.pack(fill=tk.X, expand=1)

        finish = tk.Button(self, text=msg.EX_FINISH,command=self._finalize)
        finish.pack(fill=tk.X)

        self.state = tk.StringVar()
        self.info = tk.Label(self, textvariable=self.state)
        self.info.pack(fill=tk.X)

    def _updateDescription(self, event):
        """ updates the description variable if the field is changed. """

        self.description = event.widget.get("0.0", tk.END)

    def _addVariable(self, load=False):
        """ Adding a trait variable 
        
        Args:
            load (bool): set true if called while parsing an existing trait.
            
        """

        var = VarFrame(self.frame)
        self.vars.append(var)
        if not load:
            var.pack(fill=tk.X)

    def _addRank(self, load=False):
        """ Adding a rank variable 

        Args:
            load (bool): set true if called while parsing an existing trait.

        """

        rank = RankFrame(self.frame)
        self.vars.append(rank)
        if not load:
            rank.pack(fill=tk.X)

    def varUp(self, var):
        """ moving a variable up """

        index = self.vars.index(var)
        if index > 0:
            self.vars.pop(index)
            index -= 1
            self.vars.insert(index, var)
            self._redrawVars()

    def varDown(self, var):
        """ moving a variable down """

        index = self.vars.index(var)
        if index < len(self.vars) - 1:
            self.vars.pop(index)
            index += 1
            self.vars.insert(index, var)
            self._redrawVars()

    def varRemove(self, var):
        """ removing a variable"""

        index = self.vars.index(var)
        self.vars.pop(index)
        var.destroy()
        self._redrawVars()

    def _redrawVars(self):
        """ redrawing the variable frame as needed """

        # remove everything
        widgets = self.frame.winfo_children()
        for widget in widgets:
            widget.pack_forget()

        # redraw the existing variables
        for var in self.vars:
            var.pack(fill=tk.X)

        # makes sure that the frame resizes if the last variable is deleted
        if len(self.vars) == 0:
            tk.Frame(self.frame).pack()

    def _check(self):
        """ Extensive check for the data integrity of the trait 

        Returns: 
            [(str), ...] a list of errors (empty if no errors found)
        """

        errors = []

        # checking the name ...
        name = self.name.get()
        if len(name) < 1:
            errors.append(msg.EX_ERROR_NAME_EMPTY)
        elif name in self._existingNames():
            errors.append(msg.EX_ERROR_TRAIT_EXISTS)
        invalid = re.findall("[\"\'<>§&]", name)
        if len(invalid) > 0:
            errors.append(msg.EX_ERROR_NAME_INVALID)

        # checking xp
        xp = 0
        try:
            xp = int(self.xp.get())
            print(xp)
            if xp == 0:
                raise ValueError
        except ValueError:
            errors.append(msg.EX_ERROR_XP_VALUE)

        # checking spec
        spec = self.spec.get()
        invalid = re.findall("[\"\'<>§&]", spec)
        if len(invalid) > 0:
            errors.append(msg.EX_ERROR_INVALID_SPEC)

        # go through the variables and check them individually ...
        for var in self.vars:
            if type(var) == VarFrame:
                errors = self._checkVar(var, xp, errors)
            if type(var) == RankFrame:
                errors = self._checkRank(var, xp, errors)

        return errors

    @staticmethod
    def _checkVar(var, xp, errors):
        """ checks a variable for valid data 
        
        Args: 
            var (VarFrame): the variable to check
            xp (int): the base xp value for the trait
            errors [(str), ...]: List of errors already found
            
        Returns: 
            [(str), ...] a list of errors
        
        """

        # check the name
        name = var.name.get()
        invalid = re.findall("[\"\'<>§&]", name)
        if len(name) < 1 or len(invalid) > 0:
            if msg.EX_ERROR_INVALID_VAR_NAME not in errors:
                errors.append(msg.EX_ERROR_INVALID_VAR_NAME)

        # get the data
        mode = var.mode
        o_names = []
        o_vals = []
        for option in var.options:
            o_names.append(option[0].get())
            o_vals.append(option[1].get())

        # check the xp values
        for val in o_vals:
            try:
                val = float(val)
                if val == 0:
                    raise ValueError
            except ValueError:
                if msg.EX_ERROR_XP_VALUE not in errors:
                    errors.append(msg.EX_ERROR_XP_VALUE)
                val = 0

            if mode == "add":
                if xp > 0 > val:
                    if msg.EX_ERROR_NEG_ADV not in errors:
                        errors.append(msg.EX_ERROR_NEG_ADV)
                if xp < 0 < val:
                    if msg.EX_ERROR_POS_DIS not in errors:
                        errors.append(msg.EX_ERROR_POS_DIS)
            else:
                if val < 0:
                    if msg.EX_ERROR_NEG_MULT not in errors:
                        errors.append(msg.EX_ERROR_NEG_MULT)

        # check the names
        for name in o_names:
            invalid = re.findall("[\"\'<>§&,]", name)
            if len(name) < 1 or len(invalid) > 0:
                if msg.EX_ERROR_INVALID_OPTION not in errors:
                    errors.append(msg.EX_ERROR_INVALID_OPTION)

        # and number of options
        if len(o_names) < 2:
            if msg.EX_ERROR_OPTION_LENGTH not in errors:
                errors.append(msg.EX_ERROR_OPTION_LENGTH)

        return errors

    @staticmethod
    def _checkRank(var, xp, errors):
        """ Checking a rank variable for data integrity 
        
        Args: 
            var (RankFrame): the variable to check
            xp (int): the base xp value for the trait
            errors [(str), ...]: List of errors already found
            
        Returns: 
            [(str), ...] a list of errors
        
        """

        # checking the name
        name = var.name.get()
        invalid = re.findall("[\"\'<>,]", name)
        if len(name) < 1 or len(invalid) > 0:
            if msg.EX_ERROR_INVALID_RANK_NAME not in errors:
                errors.append(msg.EX_ERROR_INVALID_RANK_NAME)

        # get the data
        mode = var.mode
        min_rank = 0
        max_rank = 0
        r_xp = 0
        try:
            min_rank = int(var.min.get())
            max_rank = int(var.max.get())
            r_xp = int(var.xp.get())
        except ValueError:
            pass

        # check for rank and xp errors
        if min_rank < 1:
            if msg.EX_ERROR_RANK_MIN not in errors:
                errors.append(msg.EX_ERROR_RANK_MIN)
        if max_rank <= min_rank:
            if msg.EX_ERROR_RANK_MAX not in errors:
                errors.append(msg.EX_ERROR_RANK_MAX)

        if mode == "add":
            if xp > 0 > r_xp:
                if msg.EX_ERROR_NEG_ADV not in errors:
                    errors.append(msg.EX_ERROR_NEG_ADV)
            if xp < 0 < r_xp:
                if msg.EX_ERROR_POS_DIS not in errors:
                    errors.append(msg.EX_ERROR_POS_DIS)
        else:
            if r_xp < 0:
                if msg.EX_ERROR_NEG_MULT not in errors:
                    errors.append(msg.EX_ERROR_NEG_MULT)

        return errors

    def _finalize(self):
        """ Storing the trait and closing the window """

        # first check for errors and break if necessary
        errors = self._check()
        if errors:
            # display and return
            errors = "\n".join(errors)
            tkmb.showerror(
                msg.EX_ITEM_NOT_SAVED,
                errors,
                parent=self
            )
            return

        # clear the trait ...
        sub_elements = list(self.trait)
        for element in sub_elements:
            self.trait.remove(element)

        # now write the data ...
        # ... basics ...
        self.trait.set("name", self.name.get())
        self.trait.set("xp", self.xp.get())
        self.trait.set("group", self._traitGroupsDict()[self.group.get()])

        # ... description ...
        description = et.SubElement(
            self.trait,
            "description"
        )
        description.text = self.description

        # ... specification ...
        if len(self.spec.get()) > 0:
            et.SubElement(
                self.trait,
                "specification",
                {"name": self.spec.get()}
            )

        # now the variables
        for i, var in enumerate(self.vars, 1):
            if type(var) == VarFrame:
                var_tag = et.SubElement(
                    self.trait,
                    "variable",
                    {"name": var.name.get(),
                     "factor": var.mode,
                     "id": str(i)}
                )
                values = []
                xp = []
                for option in var.options:
                    values.append(option[0].get())
                    xp.append(option[1].get())
                value_attr = ",".join(values)
                xp = ",".join(xp)
                var_tag.set("values", value_attr)
                var_tag.set("xp", xp)

                if ":" in var.description:
                    lines = var.description.split("\n")
                    main_desc = []
                    for line in lines:
                        parts = line.split(":")
                        name = parts[0].strip()

                        if name in values:
                            description = et.SubElement(
                                var_tag,
                                "description",
                                {"value": name}
                            )
                            desc = parts[1].strip()
                            description.text = desc
                        else:
                            main_desc.append(line)
                    main_desc = "\n".join(main_desc)
                    description = et.SubElement(
                        var_tag,
                        "description"
                    )
                    description.text = main_desc
                elif len(var.description) > 1:
                    description = et.SubElement(
                        var_tag,
                        "description"
                    )
                    description.text = var.description

            if type(var) == RankFrame:
                var_tag = et.SubElement(
                    self.trait,
                    "rank",
                    {"name": var.name.get(),
                     "factor": var.mode,
                     "min": var.min.get(),
                     "max": var.max.get(),
                     "xp": var.xp.get(),
                     "id": str(i)}
                )

        # append if necessary
        traits = self.app.module.expansion.find("traits")
        if self.trait not in traits:
            traits.append(self.trait)

        # update view and close
        self.app.module.updateTraits()
        self.close()

    def _readTrait(self):
        """ parsing an existing trait """

        # first check if the trait is not new
        if self.trait.get("name") is None:
            return

        # write data to the variables
        self.name.set(self.trait.get("name"))
        self.xp.set(self.trait.get("xp"))
        grp = self._traitGroupsDict(reverse=True)[self.trait.get("group")]
        self.group.set(grp)


        # write the stuff stored in sub tags ...
        sub_tags = list(self.trait)
        for element in sub_tags:
            # reading the specification ...
            if element.tag == "specification":
                self.spec.set(element.get("name"))

            # handling variables ...
            if element.tag == "variable":
                self._addVariable(load=True)
                var = self.vars[-1]
                var.name.set(element.get("name"))
                values = element.get("values").split(",")
                xp = element.get("xp").split(",")
                var.options = []
                for value, xp_val in zip(values, xp):
                    print(value, xp_val)
                    val = tk.StringVar()
                    val.set(value)
                    xp_var = tk.StringVar()
                    xp_var.set(xp_val)
                    var.options.append([val, xp_var])
                var.showOptions()

                if element.get("factor") == "multiply":
                    var.toggleMode()

                desc = []
                descriptions = element.findall("description")
                for description in descriptions:
                    text = ""
                    if description.get("value"):
                        text = description.get("value") + ": "
                    text += description.text
                    desc.append(text)
                var.description = "\n".join(desc)

                var.toggleView()

            # handling ranks ...
            if element.tag == "rank":
                self._addRank(load=True)
                var = self.vars[-1]
                var.name.set(element.get("name"))
                var.min.set(element.get("min"))
                var.max.set(element.get("max"))
                var.xp.set(element.get("xp"))
                if element.get("factor") == "multiply":
                    var.toggleMode()

                var.toggleView()

            if element.tag == "description":
                self.description += element.text

        # show it ...
        self.desc_text.insert("0.0", self.description)
        self._redrawVars()

    @staticmethod
    def _traitGroupsDict(reverse=False):
        """ providing a dict of trait groups 
        
        Args: 
            reverse (bool): switches key and values
        
        Returns: 
            dict: trait groups 
        
        """

        tg = config.TraitGroups()
        groups = {
            msg.TS_BODY: tg.BODY,
            msg.TS_MIND: tg.MIND,
            msg.TS_SOCIAL: tg.SOCIAL,
            msg.TS_PERCEPTION: tg.PERCEPTION,
            msg.TS_FINANCIAL: tg.FINANCIAL,
            msg.TS_FIGHTING: tg.FIGHTING,
            msg.TS_ILLNESS: tg.ILLNESS,
            msg.TS_TEMPORAL: tg.TEMPORAL,
            msg.TS_SKILL: tg.SKILL,
            msg.TS_BEHAVIOR: tg.BEHAVIOR,
            msg.TS_XS: tg.XS,
            msg.TS_PSI: tg.PSI
        }

        if reverse:
            groups = {v: k for k, v in groups.items()}

        return groups

    @staticmethod
    def _traitGroupsList():
        """ providing a (sorted) list of trait group names 
        
        Returns: 
            list: names of trait groups
        """

        groups = [
            msg.TS_BODY,
            msg.TS_MIND,
            msg.TS_SOCIAL,
            msg.TS_PERCEPTION,
            msg.TS_FINANCIAL,
            msg.TS_FIGHTING,
            msg.TS_ILLNESS,
            msg.TS_TEMPORAL,
            msg.TS_SKILL,
            msg.TS_BEHAVIOR,
            msg.TS_XS,
            msg.TS_PSI,
        ]
        return groups

    def close(self):
        """ closes the window """

        self.app.open_windows["skill"] = 0
        self.destroy()


class VarFrame(tk.Frame):
    """ A complex widget storing and displaying data for a trait variable """

    def __init__(self, master=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.master = master
        self.name = tk.StringVar()
        self.options = [
            [tk.StringVar(), tk.StringVar()],
            [tk.StringVar(), tk.StringVar()],
        ]
        self.description = ""

        self.mode = "add"
        self.remove_icon = ImageTk.PhotoImage(file="img/del_s.png")
        self.add_icon = ImageTk.PhotoImage(file="img/plus_s.png")
        self.plus_icon = ImageTk.PhotoImage(file="img/plus1_s.png")
        self.mult_icon = ImageTk.PhotoImage(file="img/multi1_s.png")
        self.up_icon = ImageTk.PhotoImage(file="img/up_s.png")
        self.down_icon = ImageTk.PhotoImage(file="img/down_s.png")
        self.min_icon = ImageTk.PhotoImage(file="img/minimize_s.png")

        self.full = tk.LabelFrame(self, text=msg.EX_VARIABLE)
        frame = tk.Frame(self.full)
        self.mode_button = tk.Button(
            frame,
            image=self.plus_icon,
            command=self.toggleMode
        )
        ToolTip(self.mode_button, msg.EX_TT_SWITCH_MODE, "info")
        self.mode_button.pack(side=tk.LEFT)
        name_entry = tk.Entry(frame, textvariable=self.name)
        name_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        def checkName(var, tt):
            """ inline check for the given name """

            name = var.get()
            invalid = re.findall("[\"\'§<>&]", name)

            if len(name) < 1:
                tt.update(msg.EX_TT_TRAIT_NAME, "error")
            elif len(invalid) > 0:
                tt.update(msg.EX_TT_NAME_INVALID, "error")
                tt.widget.config(style="invalid.TEntry")
            else:
                tt.update(msg.EX_TT_NAME_OKAY, "okay")
                tt.widget.config(style="TEntry")

        tt = ToolTip(name_entry, msg.EX_TT_VAR_NAME, "info")
        self.name.trace(
            "w",
            lambda n, e, m, v=self.name, tt=tt:
                checkName(v, tt)
        )

        toplevel = self.winfo_toplevel()
        d_label = tk.Label(frame, image=self.down_icon)
        d_label.bind(
            "<Button-1>",
            lambda event, var=self: toplevel.varDown(var)
        )
        ToolTip(d_label, msg.EX_TT_MOVE_DOWN)
        d_label.pack(side=tk.LEFT)
        u_label = tk.Label(frame, image=self.up_icon)
        u_label.bind(
            "<Button-1>",
            lambda event, var=self: toplevel.varUp(var)
        )
        ToolTip(u_label, msg.EX_TT_MOVE_DOWN)
        u_label.pack(side=tk.LEFT)
        m_label = tk.Label(frame, image=self.min_icon)
        m_label.pack(side=tk.LEFT)
        m_label.bind(
            "<Button-1>",
            lambda event: self.toggleView()
        )
        ToolTip(m_label, msg.EX_TT_MINIMIZE)

        x_label = tk.Label(frame, image=self.remove_icon)
        x_label.bind(
            "<Button-1>",
            lambda event, var=self: toplevel.varRemove(var)
        )
        ToolTip(x_label, msg.EX_TT_DEL_VAR, "info")
        x_label.pack(side=tk.LEFT)
        frame.pack(fill=tk.X, expand=1)

        self.option_frame = tk.Frame(self.full)
        self.option_frame.pack(fill=tk.X, expand=1)
        self.option_frame.columnconfigure(0, weight=100)
        self.showOptions()

        desc_frame = tk.LabelFrame(self.full, text=msg.EX_DESCRIPTION)
        self.desc_text = tk.Text(desc_frame,width=10, height=5)
        self.desc_text.pack(fill=tk.BOTH, expand=1)
        self.desc_text.bind("<KeyRelease>", self._updateDescription)
        desc_frame.pack(fill=tk.X)
        self.full.pack(fill=tk.X, expand=1)

        self.button = tk.Button(
            self,
            textvariable=self.name,
            command=self.toggleView
        )
        ToolTip(self.button, msg.EX_TT_RESTORE)

    def _updateDescription(self, event):
        """ updates the stored description, when the field changes. """

        self.description = event.widget.get("0.0", tk.END)

    def toggleView(self):
        """ Minimizing to button or restoring full view """

        if self.button.winfo_viewable():
            self.button.pack_forget()
            self.desc_text.delete("0.0", tk.END)
            self.desc_text.insert("0.0", self.description)
            self.full.pack(fill=tk.X)
        else:
            self.full.pack_forget()
            self.button.pack(fill=tk.X)

    def showOptions(self):
        """ Displaying the current options """

        def checkName(var, tt):
            """ inline check for the given name, run as a trace on the variable 
            
            Note: 
                Modifies widget style and tooltip 
            
            """

            name = var.get()
            invalid = re.findall("[\"\'§<>&]", name)

            if len(name) < 1:
                tt.update(msg.EX_TT_TRAIT_NAME, "error")
            elif len(invalid) > 0:
                tt.update(msg.EX_TT_NAME_INVALID, "error")
                tt.widget.config(style="invalid.TEntry")
            else:
                tt.update(msg.EX_TT_NAME_OKAY, "okay")
                tt.widget.config(style="TEntry")

        def checkXP(var, tt):
            """ inline check on the XP value. Run as a trace on the variable 
                        
            Note: 
                Modifies widget style and tooltip 

            """

            p_xp = self.winfo_toplevel().xp.get()
            try:
                p_xp = float(p_xp)
            except ValueError:
                p_xp = 0

            xp = var.get()
            if "," in xp:
                xp = xp.replace(",", ".")
                var.set(xp)
            try:
                xp = float(xp)
                if xp == 0:
                    raise ValueError

                if self.mode == "add":
                    if p_xp < 0 < xp:
                        tt.update(msg.EX_TT_POS_DIS, "error")
                        tt.widget.config(style="invalid.TEntry")
                    if p_xp > 0 > xp:
                        tt.update(msg.EX_TT_NEG_ADV, "error")
                        tt.widget.config(style="invalid.TEntry")
                    else:
                        tt.update(msg.EX_TT_XP_OKAY, "okay")
                        tt.widget.config(style="TEntry")
                else:
                    if xp < 0:
                        tt.update(msg.EX_TT_NEG_MULT, "error")
                        tt.widget.config(style="invalid.TEntry")
                    else:
                        tt.update(msg.EX_TT_XP_OKAY, "okay")
                        tt.widget.config(style="TEntry")

            except ValueError:
                tt.widget.config(style="invalid.TEntry")
                tt.update(msg.EX_TT_INVALID_XP, "error")

        # clear the frame
        widgets = self.option_frame.winfo_children()
        for widget in widgets:
            widget.destroy()

        # draw the header
        tk.Label(self.option_frame, text=msg.EX_NAME).grid(row=0, column=0)
        tk.Label(self.option_frame, text=msg.XP).grid(row=0, column=1)
        add_button = tk.Label(self.option_frame, image=self.add_icon)
        add_button.grid(row=0, column=2)
        add_button.bind("<Button-1>", lambda event: self._addOption())
        ToolTip(add_button, msg.EX_TT_ADD_OPTION, "info")

        # go through the options and render them
        for i, option in enumerate(self.options):
            name_entry = tk.Entry(
                self.option_frame,
                textvariable=self.options[i][0]
            )
            tt = ToolTip(name_entry, msg.EX_TT_OPTION_NAME, "info")
            self.options[i][0].trace(
                "w",
                lambda n, e, m, v=self.options[i][0], tt=tt:
                    checkName(v, tt)
            )
            name_entry.grid(row=i + 1, column=0, sticky=tk.NSEW)
            xp_entry = tk.Entry(
                self.option_frame,
                textvariable=self.options[i][1],
                width=4
            )
            tt = ToolTip(xp_entry, msg.EX_TT_OPTION_XP, "info")
            self.options[i][1].trace(
                "w",
                lambda n, e, m, v=self.options[i][1], tt=tt:
                    checkXP(v, tt)
            )

            xp_entry.grid(row=i + 1, column=1, sticky=tk.NSEW)
            del_button = tk.Label(
                self.option_frame,
                image=self.remove_icon,
            )
            del_button.grid(row=i + 1, column=2)
            del_button.bind(
                "<Button-1>",
                lambda event, entry=i: self._delOption(entry)
            )
            ToolTip(del_button, msg.EX_TT_DEL_OPTION, "info")

    def _delOption(self, entry):
        """ Removes an option and redraws the widgets """

        self.options.pop(entry)
        self.showOptions()

    def _addOption(self):
        """ Adds a new option and redraws the widgets """

        self.options.append([tk.StringVar(), tk.StringVar()])
        self.showOptions()

    def toggleMode(self):
        """ toggles between add and multiply mode """

        if self.mode == "add":
            self.mode = "multiply"
            self.mode_button.config(image=self.mult_icon)
        else:
            self.mode = "add"
            self.mode_button.config(image=self.plus_icon)


class RankFrame(tk.Frame):
    """ A complex widget storing and displaying data for a rank variable. """

    def __init__(self, master=None, **kwargs):
        super().__init__(master=master, **kwargs)
        self.master = master
        self.name = tk.StringVar()
        self.min = tk.StringVar()
        self.max = tk.StringVar()
        self.xp = tk.StringVar()
        self.mode = "add"

        self.plus_icon = ImageTk.PhotoImage(file="img/plus1_s.png")
        self.mult_icon = ImageTk.PhotoImage(file="img/multi1_s.png")
        self.remove_icon = ImageTk.PhotoImage(file="img/del_s.png")
        self.up_icon = ImageTk.PhotoImage(file="img/up_s.png")
        self.down_icon = ImageTk.PhotoImage(file="img/down_s.png")
        self.min_icon = ImageTk.PhotoImage(file="img/minimize_s.png")

        def checkName(var, tt):
            """ inline check for name - run as a trace 
            
            Note: 
                sets widget style and tooltip 
            """

            name = var.get()
            invalid = re.findall("[\"\'§<>&]", name)

            if len(name) < 1:
                tt.update(msg.EX_TT_TRAIT_NAME, "error")
            elif len(invalid) > 0:
                tt.update(msg.EX_TT_NAME_INVALID, "error")
                tt.widget.config(style="invalid.TEntry")
            else:
                tt.update(msg.EX_TT_NAME_OKAY, "okay")
                tt.widget.config(style="TEntry")

        def checkXP(tt):
            """ inline check for xp values - run as a trace 
                        
            Note: 
                sets widget style and tooltip 
            """

            min_rank = self.min.get()
            max_rank = self.max.get()
            xp = self.xp.get()
            error = []
            p_xp = self.winfo_toplevel().xp.get()
            try:
                p_xp = int(p_xp)
            except ValueError:
                p_xp = 0

            try:
                xp = int(xp)
                min_rank = int(min_rank)
                max_rank = int(max_rank)

                if min_rank < 1:
                    error.append(msg.EX_TT_MIN_RANK)
                if max_rank < min_rank:
                    error.append(msg.EX_TT_MAX_RANK)

                if self.mode == "add":
                    if p_xp < 0 < xp:
                        error.append(msg.EX_TT_POS_DIS)

                    if p_xp > 0 > xp:
                        error.append(msg.EX_TT_NEG_ADV)
                    else:
                        pass
                else:
                    if xp < 0:
                        error.append(msg.EX_TT_NEG_MULT)
                    else:
                        pass

                if xp == 0:
                    raise ValueError
            except ValueError:
                error.append(msg.EX_TT_INVALID_RANKS)

            entries = []
            widgets = tt.widget.winfo_children()
            for widget in widgets:
                entries.append(widget.winfo_children()[0])

            if error:
                for entry in entries:
                    entry.config(style="invalid.TEntry")
                tt.update("\n".join(error), "error")
            else:
                for entry in entries:
                    entry.config(style="TEntry")
                tt.update(msg.EX_TT_RANKS_OKAY, "okay")

        self.full = tk.LabelFrame(self, text=msg.EX_RANK)
        frame = tk.Frame(self.full)
        self.mode_button = tk.Button(
            frame,
            image=self.plus_icon,
            command=self.toggleMode
        )
        self.mode_button.pack(side=tk.LEFT)
        ToolTip(self.mode_button, msg.EX_TT_SWITCH_MODE, "info")

        name_entry = tk.Entry(frame, textvariable=self.name)
        tt = ToolTip(name_entry, msg.EX_TT_VAR_NAME, "info")
        self.name.trace(
            "w",
            lambda n, e, m, var=self.name, tt=tt: checkName(var, tt)
        )
        name_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        toplevel = self.winfo_toplevel()
        d_label = tk.Label(frame, image=self.down_icon)
        d_label.bind(
            "<Button-1>",
            lambda event, var=self: toplevel.varDown(var)
        )
        ToolTip(d_label, msg.EX_TT_MOVE_DOWN)
        d_label.pack(side=tk.LEFT)
        u_label = tk.Label(frame, image=self.up_icon)
        u_label.bind(
            "<Button-1>",
            lambda event, var=self: toplevel.varUp(var)
        )
        ToolTip(u_label, msg.EX_TT_MOVE_UP)
        u_label.pack(side=tk.LEFT)
        m_label = tk.Label(frame, image=self.min_icon)
        m_label.pack(side=tk.LEFT)
        m_label.bind(
            "<Button-1>",
            lambda event: self.toggleView()
        )
        ToolTip(m_label, msg.EX_TT_MINIMIZE)
        x_label = tk.Label(frame, image=self.remove_icon)
        x_label.bind(
            "<Button-1>",
            lambda event, var=self: toplevel.varRemove(var)
        )
        ToolTip(x_label, msg.EX_TT_DEL_RANK)
        x_label.pack(side=tk.LEFT)
        frame.pack(fill=tk.X, expand=1)
        frame.pack(fill=tk.X, expand=1)

        frame = tk.Frame(self.full)
        tt = ToolTip(frame, msg.EX_TT_RANKS, "info")
        self.min.trace(
            "w",
            lambda n, e, m, tt=tt: checkXP(tt)
        )
        self.max.trace(
            "w",
            lambda n, e, m, tt=tt: checkXP(tt)
        )
        self.xp.trace(
            "w",
            lambda n, e, m, tt=tt: checkXP(tt)
        )

        min_frame = tk.LabelFrame(frame, text=msg.EX_MIN_RANK)
        min_entry = tk.Entry(
            min_frame,
            textvariable=self.min,
            width=4
        )
        min_entry.pack(fill=tk.X, expand=1)
        min_frame.pack(side=tk.LEFT, fill=tk.X, expand=1)
        
        max_frame = tk.LabelFrame(frame, text=msg.EX_MAX_RANK)
        max_entry = tk.Entry(
            max_frame,
            textvariable=self.max,
            width=4
        )
        max_entry.pack(fill=tk.X, expand=1)
        max_frame.pack(side=tk.LEFT, fill=tk.X, expand=1)

        xp_frame = tk.LabelFrame(frame, text=msg.XP)
        xp_entry = tk.Entry(
            xp_frame,
            textvariable=self.xp,
            width=4
        )
        xp_entry.pack(fill=tk.X, expand=1)
        xp_frame.pack(side=tk.LEFT, fill=tk.X, expand=1)
        frame.pack(fill=tk.X, expand=1)
        self.full.pack(fill=tk.X, expand=1)

        self.button = tk.Button(
            self,
            textvariable=self.name,
            command=self.toggleView
        )
        ToolTip(self.button, msg.EX_TT_RESTORE)

    def toggleView(self):
        """ Minimizing to button or restoring full view """

        if self.button.winfo_viewable():
            self.button.pack_forget()
            self.full.pack(fill=tk.X)
        else:
            self.full.pack_forget()
            self.button.pack(fill=tk.X)

    def toggleMode(self):
        """ toggles between add and multiply mode """

        if self.mode == "add":
            self.mode = "multiply"
            self.mode_button.config(image=self.mult_icon)
        else:
            self.mode = "add"
            self.mode_button.config(image=self.plus_icon)


class SkillCopy(tk.Frame):
    """ Provides a widget for fast creation of skills """

    def __init__(self, master=None, source=None, app=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.source = source

        self.icon_child = ImageTk.PhotoImage(file="img/child_s.png")
        self.icon_sibling = ImageTk.PhotoImage(file="img/sibling_s.png")

        self.loaded_skills = None
        self.mode = "sibling"

        self.skill = et.Element("skill")

        self.toggle_button=tk.Button(
            self,
            image=self.icon_sibling,
            command=self._toggleMode
        )
        self.toggle_button.pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        self.name_var.trace("w", self._updateName)
        self.name_entry = tk.Entry(self, textvariable=self.name_var)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.okay_button = tk.Button(
            self,
            text="OK",
            width=4,
            command=self._create
        )
        self.okay_button.pack(side=tk.LEFT)

    def config(self, **kwargs):
        self.toggle_button.config(**kwargs)
        self.name_entry.config(**kwargs)
        self.okay_button.config(**kwargs)

    def updateSource(self, source):
        self.source = source
        self.name_var.set(source.get("name"))
        self.loaded_skills = self._list()

    def _updateName(self, *args):
        name = self.name_var.get()

        if not self.loaded_skills:
            self.loaded_skills = self._list()

        invalid = re.findall("[\"\'§&]", name)
        if name in self.loaded_skills:
            self.name_entry.config(style="invalid.TEntry")
            self.okay_button.config(state=tk.DISABLED)
        elif len(invalid) > 0:
            self.name_entry.config(style="invalid.TEntry")
            self.okay_button.config(state=tk.DISABLED)
        else:
            self.name_entry.config(style="TEntry")
            self.okay_button.config(state=tk.NORMAL)
            self.skill.set("name", name)

    def _list(self):
        """ get a list of all used skill names """

        cur = [s[0] for s in self.app.skills.getList()]
        exp = self.app.module.expansion.findall(".//skill")
        exp = [s.get("name") for s in exp]
        return cur + exp

    def _create(self):
        if self.mode == "sibling":
            spec = self.source.get("spec")
            self.skill.set("spec", spec)
            self.skill.set("parent", self.source.get("parent"))
            self.skill.set("type", self.source.get("type"))
            spec = int(spec)
            if spec == 2:
                self.skill.set("id", str(int(self.source.get("id")) + 100))
            if spec == 3:
                self.skill.set("id", str(int(self.source.get("id")) + 1))

        else:
            spec = self.source.get("spec")
            spec = int(spec) + 1
            self.skill.set("spec", str(spec))
            self.skill.set("parent", self.source.get("id"))
            self.skill.set("type", self.source.get("type"))
            id = int(self.source.get("id")) + 1
            while id in self._expansionSkillIDs():
                id += 1
            self.skill.set("id", str(id))

        skills = self.app.module.expansion.find("skills")
        skills.append(self.skill)
        self.app.module.updateSkills()

        if spec == 3 and self.mode == "child":
            self._toggleMode()
        self.updateSource(self.skill)
        self.skill = et.Element("skill")

    def _expansionSkillIDs(self):
        exp_skills = self.app.module.expansion.findall(".//skill")
        return [int(s.get("id")) for s in exp_skills]

    def _toggleMode(self):
        if self.source is None:
            return

        if self.mode == "sibling" and self.source.get("spec") in ["1", "2"]:
            self.mode = "child"
            self.toggle_button.config(image=self.icon_child)
        else:
            self.mode = "sibling"
            self.toggle_button.config(image=self.icon_sibling)
