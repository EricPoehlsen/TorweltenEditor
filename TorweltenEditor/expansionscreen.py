import tk_ as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
import config
from PIL import ImageTk
import os
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

        self.rowconfigure(0, weight=100)
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.toolbar = tk.Frame(self)
        self.toolbar.grid(row=1, column=0, sticky=tk.NSEW)
        self.showToolbar(self.toolbar)
        trait_frame = self.showTraits(self.frame)
        skill_frame = self.showSkills(self.frame)
        item_frame = self.showItems(self.frame)
        trait_frame.pack(side=tk.LEFT, anchor=tk.N)
        skill_frame.pack(side=tk.LEFT, anchor=tk.N)
        item_frame.pack(side=tk.LEFT, anchor=tk.N)

    def showTraits(self, frame):
        trait_frame = tk.LabelFrame(frame, text=msg.EX_TRAITS)
        list_frame = tk.Frame(trait_frame)
        self.widgets["traits"] = trait_list = tk.Listbox(list_frame)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=trait_list.yview)
        trait_list.config(yscrollcommand=scroll.set)
        trait_list.pack(side=tk.LEFT)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack()
        button=tk.Button(
            trait_frame,
            text="edit trait",
            command=self._editTrait
        )
        button.pack()

        return trait_frame

    def showSkills(self, frame):
        skill_frame = tk.LabelFrame(frame, text=msg.EX_SKILLS)
        list_frame = tk.Frame(skill_frame)
        self.widgets["skills"] = skill_list = tk.Listbox(list_frame)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=skill_list.yview)
        skill_list.config(yscrollcommand=scroll.set)
        skill_list.pack(side=tk.LEFT)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack()

        add = tk.Button(
            skill_frame,
            text=msg.EX_NEW,
            command=self._addSkill
        )
        add.pack(fill=tk.X)
        edit = tk.Button(
            skill_frame,
            text=msg.EX_EDIT,
            command=self._editSkill
        )
        edit.pack(fill=tk.X)
        remove = tk.Button(
            skill_frame,
            text=msg.EX_DEL,
            command=self._delSkill
        )
        remove.pack(fill=tk.X)

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
        self.widgets["items"] = item_list = tk.Listbox(list_frame)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=item_list.yview)
        item_list.config(yscrollcommand=scroll.set)
        item_list.pack(side=tk.LEFT)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack()
        button = tk.Button(
            item_frame,
            text="edit items",
            command=self._editItem
        )
        button.pack()

        self.updateItems()
        return item_frame

    def updateItems(self):
        listbox = self.widgets["items"]
        items = self.expansion.findall(".//item")
        listbox.delete(0, tk.END)
        l = [i.get("name") for i in items]
        listbox.insert(0, *l)

    def showToolbar(self, frame):

        exp_ops = [
            (msg.EX_TT_NEW, "img/tpl_new.png", self._newExpansion),
            (msg.EX_TT_LOAD, "img/tpl_load.png", self._loadExpansion),
            (msg.EX_TT_SAVE, "img/tpl_save.png", self._saveExpansion)
        ]

        exp = tk.LabelFrame(frame, text="Expansion")
        for op in exp_ops:
            img = ImageTk.PhotoImage(file=op[1])
            button = tk.Button(
                exp,
                text=op[0],
                image=img,
                command=op[2],
            )
            tt = ToolTip(button, op[0])
            button.image = img
            button.pack(side=tk.LEFT)
        exp.pack(side=tk.LEFT)

        tk.Label(frame, text=" ").pack(side=tk.LEFT)

    def _editItem(self, event=None):
        if event:
            pass
        a = ItemEditor(None, self.app, None)

    def _editTrait(self):
        a = TraitEditor(None, self.app, None)

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
            'initialdir': './data',
            'initialfile': 'template.xml',
            'parent': self,
            'title': 'Charakterbogentemplate laden ...',
        }
        filename = tkfd.askopenfilename(**options)
        if filename:
            with open(filename, mode="rb") as file:
                expansion = et.parse(file)
                root = expansion.getroot()
                if root.tag == "expansion":
                    self.expansion = expansion
        else:
            pass

    def _saveExpansion(self):
        """ save the current expansion to disk """

        options = {
            "defaultextension": ".xml",
            "filetypes": [("Template", ".xml")],
            "initialdir": "./data",
            "initialfile": "template.xml",
            "parent": self,
            "title": "Charakterbogentemplate speichern ...",
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

        self.item = item

        if self.item is None:
            self.item = et.Element("item")

        self.page = 1
        self._setName()

    def _clear(self):
        widgets = self.winfo_children()
        for widget in widgets:
            widget.destroy()

    def _setName(self):
        """ first step of item creation name and item type """
        self._clear()

        if self.data.get("name"):
            name = self.data["name"]
        else:
            self.data["name"] = name = tk.StringVar()

        if self.item.get("name"):
            name.set(self.item.get("name"))

        name.trace("w", lambda n, e, m, var=name: self._checkName(var))

        name_frame = tk.LabelFrame(self, text=msg.NAME)
        entry = tk.Entry(name_frame, textvariable=name)
        entry.pack(fill=tk.X, expand=1)
        name_frame.pack(fill=tk.X, expand=1)

        type_frame = tk.LabelFrame(self, text=msg.EX_ITEM_TYPE)
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

        self.c_button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._nextPage
        )
        self.c_button.pack(fill=tk.X)

        return True

    def _updateTypes(self, var):
        selected = var.get()

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

        try:
            value = None
            if self.data.get("type"):
                value = self.data["type"].get()
            if not value or value not in groups[selected]:
                value = groups[selected][0]
            self.tp.set_menu(value, *groups[selected])

        except tk.TclError:
            pass

    def _checkName(self, var):
        """ make sure no item with this name exists ... """
        pass

    def _basicData(self):
        self._clear()
        tk.Label(
            self,
            text=self.data["name"].get(),
            font="Arial 12 bold"
        ).pack()
        tk.Label(self, text=self.data["type"].get()).pack()

        if self.data.get("price"):
            price = self.data["price"]
        else: 
            self.data["price"] = price = tk.StringVar()
            price.set("0")
        if self.data.get("weight"):
            weight = self.data["weight"]
        else: 
            self.data["weight"] = weight = tk.StringVar()
            weight.set("0")
        if self.data.get("avail"):
            avail = self.data["avail"]
        else:
            self.data["avail"] = avail = tk.StringVar()
            avail.set("0")

        p_frame = tk.LabelFrame(self, text=msg.EX_ITEM_PRICE)
        self.p_entry = tk.Entry(p_frame, textvariable=price)
        self.p_entry.pack(fill=tk.X, expand=1)
        p_frame.pack(fill=tk.X)

        w_frame = tk.LabelFrame(self, text=msg.EX_ITEM_WEIGHT)
        self.w_entry = tk.Entry(w_frame, textvariable=weight)
        self.w_entry.pack(fill=tk.X, expand=1)
        w_frame.pack(fill=tk.X)
    
        a_frame = tk.LabelFrame(self, text=msg.EX_ITEM_AVAIL)
        self.a_entry = tk.Entry(a_frame, textvariable=avail)
        self.a_entry.pack(fill=tk.X, expand=1)
        a_frame.pack(fill=tk.X)

        self.c_button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._nextPage
        )
        self.c_button.pack()
        self.b_button = tk.Button(
            self,
            text=msg.EX_BACK,
            command=self._lastPage
        )
        self.b_button.pack()

        price.trace("w", lambda n, e, m, var=price: self._priceCheck(var))
        weight.trace("w", lambda n, e, m, var=weight: self._weightCheck(var))
        avail.trace("w", lambda n, e, m, var=avail: self._availCheck(var))

        return True

    def _priceCheck(self, var):
        price = var.get()
        try:
            price = price.replace(",", ".")
            price = float(price)
            if price < 0: raise ValueError
            self.p_entry.config(style="TEntry")
        except ValueError:
            self.p_entry.config(style="invalid.TEntry")

    def _weightCheck(self, var):
        weight = var.get()
        try:
            weight = int(weight)
            if weight < 0: raise ValueError
            self.w_entry.config(style="TEntry")
        except ValueError:
            self.w_entry.config(style="invalid.TEntry")

    def _availCheck(self, var):
        avail = var.get()
        try:
            avail = int(avail)
            if not -6 <= avail <= 6: raise ValueError
            self.a_entry.config(style="TEntry")
        except ValueError:
            self.a_entry.config(style="invalid.TEntry")

    def _addDamage(self):
        """ add weapon properties ... """

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

        selected_type = self.data["type"].get()

        if selected_type not in damage_types + caliber_types:
            return False

        self._clear()

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

        self.c_button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._nextPage
        )
        self.c_button.pack()
        self.b_button = tk.Button(
            self,
            text=msg.EX_BACK,
            command=self._lastPage
        )
        self.b_button.pack()

        return True

    def _checkDamage(self, var):
        damage = var.get()
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

            self.d_entry.config(style="TEntry")
        except ValueError:
            self.d_entry.config(style="invalid.TEntry")

    def _addContainer(self):
        self._clear()

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
        name_frame = tk.LabelFrame(self, text=msg.NAME)
        n_entry = tk.Entry(name_frame, textvariable=name)
        n_entry.pack(fill=tk.X, expand=1)
        name_frame.pack(fill=tk.X, expand=1)
        frame = tk.Frame(self)
        size_frame = tk.LabelFrame(frame, text=msg.EX_CONTAINER_SIZE)
        self.s_entry = tk.Entry(size_frame, textvariable=size)
        self.s_entry.pack(fill=tk.X, expand=1)
        size_frame.grid(row=0, column=0, sticky=tk.NSEW)
        limit_frame = tk.LabelFrame(frame, text=msg.EX_CONTAINER_LIMIT)
        self.l_entry = tk.Entry(limit_frame, textvariable=limit)
        self.l_entry.pack(fill=tk.X, expand=1)
        limit_frame.grid(row=0, column=1, sticky=tk.NSEW)
        frame.pack(fill=tk.X, expand=1)

        limit.trace("w", lambda n, e, m: self._checkContainer())
        size.trace("w", lambda n, e, m: self._checkContainer())

        self.c_button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._nextPage
        )
        self.c_button.pack()
        self.b_button = tk.Button(
            self,
            text=msg.EX_BACK,
            command=self._lastPage
        )
        self.b_button.pack()

        return True

    def _checkContainer(self):
        try:
            limit = self.data["container_limit"].get()
            limit = int(limit)
            if limit < 0:
                raise ValueError
            self.l_entry.config(style="TEntry")
        except ValueError:
            self.l_entry.config(style="invalid.TEntry")

        try:
            size = self.data["container_size"].get()
            size = int(size)
            if size < 0:
                raise ValueError
            self.s_entry.config(style="TEntry")
        except ValueError:
            self.s_entry.config(style="invalid.TEntry")

    def _addDescription(self):
        self._clear()
        if self.data.get("description"):
            desc = self.data["description"]
        else:
            self.data["description"] = desc = ""

        textfield = tk.Text(
            self,
            width=20,
            height=8,
            wrap=tk.WORD,

        )
        textfield.insert("0.0", desc)
        textfield.bind("<KeyRelease>", self._updateDescription)
        textfield.pack()

        self.c_button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._nextPage
        )
        self.c_button.pack()
        self.b_button = tk.Button(
            self,
            text=msg.EX_BACK,
            command=self._lastPage
        )
        self.b_button.pack()

        return True

    def _updateDescription(self, event):
        self.data["description"] = event.widget.get("0.0", tk.END)

    def _addMenuPosition(self):

        self._clear()

        selector_list_frame = tk.LabelFrame(self, text=msg.EX_MENU_POS)
        self.selector_list = tk.Treeview(
            selector_list_frame,
            selectmode=tk.BROWSE,
            show="tree",
            height=8
        )
        self.selector_list.bind("<<TreeviewSelect>>", self._menuSelect)
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
        for group in groups:
            group_id = group.get("id", "0")
            parent_id = group.get("parent", "")
            parent = nodes.get(parent_id, "")
            nodes[group_id] = self.selector_list.insert(
                parent,
                1000,
                image=self.foldericon,
                text=group.get("name", "...")
            )

        self.c_button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._nextPage
        )
        self.c_button.pack()
        self.b_button = tk.Button(
            self,
            text=msg.EX_BACK,
            command=self._lastPage
        )
        self.b_button.pack()

        return True

    def _menuSelect(self, event):
        if self.data.get("menu"):
            menu = self.data["menu"]
        else:
            self.data["menu"] = menu = tk.StringVar()

    def _finalizeItem(self):
        name = self.data["name"].get()
        weight = self.data["weight"].get()
        price = self.data["price"].get()
        avail = self.data["avail"].get()
        item_type = self._itemtypes()[self.data["type"].get()]
        self.item.set("name", name)
        self.item.set("weight", weight)
        self.item.set("price", price)
        self.item.set("avail", avail)
        self.item.set("type", item_type)

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

        if self.data.get("container"):
            if self.data["container"].get() == 1:
                container_tag = self.item.find("container")
                c_name = self.data["container_name"].get()
                limit = self.data["container_limit"].get()
                size = self.data["container_size"].get()

                if container_tag is not None:
                    container_tag.set("name", c_name)
                    container_tag.set("size", size)
                    container_tag.set("limit", limit)
                else:
                    et.SubElement(
                        self.item,
                        "container",
                        {"name": c_name,
                         "size": size,
                         "limit": limit}
                    )

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

        """
        rev_types = {v: k for k, v in types.items()}
        """

    def _nextPage(self):
        self.page += 1
        try:
            pages = {
                1: self._setName,
                2: self._basicData,
                3: self._addDamage,
                4: self._addContainer,
                5: self._addDescription,
                6: self._addMenuPosition,
                7: self._finalizeItem,

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
                1: self._setName,
                2: self._basicData,
                3: self._addDamage,
                4: self._addContainer,
                5: self._addDescription,
                6: self._addMenuPosition,
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
        self.skill = skill
        if self.skill is None:
            self.skill = et.Element("skill")

        self.loaded_skills = self._list()

        self.data = {}

        self.minsize(200, 100)
        self._nameSkill()

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

    def _nameSkill(self):
        """ first step, give it a name ..."""

        self._clear()

        # the button is declared here because the var.trace() will call it
        self.button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._selectParent
        )

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
        self.button.pack(fill=tk.X)

    def _checkName(self, var):
        """ disables 'continue button' if name exists """

        cur_name = var.get()
        if cur_name in self.loaded_skills:
            self.button.config(text=msg.EX_SKILL_EXISTS)
            self.button.state(["disabled"])
        else:
            self.button.config(text=msg.EX_CONTINUE)
            self.button.state(["!disabled"])

    def _selectParent(self):
        """ next step, select parent skill """

        self._clear()
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
        tk.Button(
            super_frame,
            text=msg.EX_CONTINUE,
            command=self._finalizeSkill
        ).pack(fill=tk.X)
        tk.Button(
            super_frame,
            text=msg.EX_BACK,
            command=self._nameSkill
        ).pack(fill=tk.X)

        super_frame.pack(fill=tk.BOTH)

        # fill the list
        skills = self.app.skills.getList(maxspec=2)
        l = [s[0] if s[1] == 1 else "    "+s[0] for s in skills]
        self.skill_list.insert(0, *l)

        # select parent, if it is an edit
        if var.get() in l:
            index = l.index(var.get())
            self.skill_list.select_set(index)
        if "    "+var.get() in l:
            index = l.index("    "+var.get())
            self.skill_list.select_set(index)

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
            self.data["parent"] = parent_id = int(self.parent.get("id"))
            self.skill.set("parent", str(parent_id))
            new_id = parent_id
            exists = True
            spec = int(self.parent.get("spec")) + 1
            factor = 1
            if spec == 2:
                factor = 100
            while exists is not None:
                new_id += factor
                exists = self.app.skills.getSkillById(new_id)

            skill_type = self.parent.get("type")
            types = {
                "active": msg.EX_ACTIVE_SKILL,
                "passive": msg.EX_PASSIVE_SKILL,
                "lang": msg.EX_LANGUAGE_SKILL
            }
            specs = {
                2: msg.EX_SPEC2,
                3: msg.EX_SPEC3
            }

            self._clear()

            # from here we build the new display
            frame = tk.LabelFrame(self, text=msg.EX_NEW_SKILL)
            name = self.data["name"].get()
            self.skill.set("name", name)
            tk.Label(
                frame,
                text=name,
                font="Arial 12 bold"
            ).pack(anchor=tk.CENTER)
            tk.Label(
                frame,
                text=types[skill_type]
            ).pack(anchor=tk.CENTER)
            tk.Label(
                frame,
                text=specs[spec] + super_name
            ).pack(anchor=tk.CENTER)

            # the id is editable but disabled ...
            id_frame = tk.Frame(frame)
            tk.Label(id_frame, text=msg.EX_ID).pack(side=tk.LEFT)
            if self.data.get("id"):
                id_var = self.data["id"]
            else:
                self.data["id"] = id_var = tk.StringVar()
            id_var.set(str(new_id))
            id_entry = tk.Entry(
                id_frame,
                textvariable=id_var,
                style="edit_entry",
                width="7"
            )
            id_entry.state(["disabled"])

            def enable(event):
                event.widget.state(["!disabled"])
            id_entry.bind(
                "<Double-Button-1>",
                enable
            )

            id_entry.pack(side=tk.LEFT)
            id_frame.pack()

            frame.pack(fill=tk.BOTH)

            tk.Button(
                self,
                text=msg.EX_FINISH,
                command=self._addSkill
            ).pack(fill=tk.X)
            tk.Button(
                self,
                text=msg.EX_BACK,
                command=self._selectParent
            ).pack(fill=tk.X)
            tk.Button(
                self,
                text=msg.EX_ABORT,
                command=self.close
            ).pack(fill=tk.X)

    def _addSkill(self):
        """ updating the final data and writing the skill to the tree """

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
    def __init__(
        self,
        master=None,
        app=None,
        trait=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.app = app
        self.trait = trait
    pass

    def close(self):
        self.app.open_windows["skill"] = 0
        self.destroy()
