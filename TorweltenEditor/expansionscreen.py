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
        trait_frame.pack(side=tk.LEFT)
        skill_frame.pack(side=tk.LEFT)
        item_frame.pack(side=tk.LEFT)

    def showTraits(self, frame):
        trait_frame = tk.Frame(frame)
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
        skill_frame = tk.Frame(frame)
        list_frame = tk.Frame(skill_frame)
        self.widgets["skills"] = skill_list = tk.Listbox(list_frame)
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll.config(command=skill_list.yview)
        skill_list.config(yscrollcommand=scroll.set)
        skill_list.pack(side=tk.LEFT)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        list_frame.pack()

        button = tk.Button(
            skill_frame,
            text="edit skills",
            command=self._editSkill
        )
        button.pack()

        return skill_frame

    def updateSkills(self):
        print("UPDATING ::::")
        listbox = self.widgets["skills"]
        skills = self.expansion.findall(".//skill")
        listbox.delete(0, tk.END)
        l = [s.get("name") for s in skills]
        print(l)
        listbox.insert(0, *l)




    def showItems(self, frame):
        item_frame = tk.Frame(frame)
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

        l = ["Test1", "Test2", "Test3"]
        item_list.insert(0, *l)

        return item_frame




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

    def _editSkill(self):
        a = SkillEditor(None, self.app, None)


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
                self.char.setPDFTemplate(filename)


class ItemEditor(tk.Toplevel):
    def __init__(
        self,
        master=None,
        app=None,
        item=None,
        expansion=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.app = app
        self.loaded_items = app.itemlist
        self.item = item
        self.expansion = expansion

        self.groups = self._getGroups()
        print(self.groups)

    def _getGroups(self):
        groups = self.loaded_items.getGroups()
        groups = [(grp.get("name"), grp.get("id")) for grp in groups]
        return groups


class SkillEditor(tk.Toplevel):
    def __init__(
        self,
        master=None,
        app=None,
        skill=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.app = app
        self.style = app.style
        self.loaded_skills = [s[0] for s in app.skills.getList()]
        self.skill = skill

        self.data = {}

        self.minsize(200, 100)
        self._nameSkill()

    def _clear(self):
        widgets = self.winfo_children()
        for widget in widgets:
            widget.destroy()

    def _nameSkill(self):
        self._clear()
        frame = tk.LabelFrame(self, text=msg.NAME)

        if self.data.get("name"):
            var = self.data.get("name")
        else:
            self.data["name"] = var = tk.StringVar()
        var.trace("w", lambda n, e, m, var=var: self._checkName(var))
        entry = tk.Entry(frame, textvariable=var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        frame.pack(fill=tk.X)
        self.button = tk.Button(
            self,
            text=msg.EX_CONTINUE,
            command=self._selectParent
        )
        self.button.pack(fill=tk.X)

    def _checkName(self, var):
        cur_name = var.get()
        if cur_name in self.loaded_skills:
            print="YAY"
            self.button.config(text=msg.EX_SKILL_EXISTS)
            self.button.state(["disabled"])
        else:
            self.button.config(text=msg.EX_CONTINUE)
            self.button.state(["!disabled"])

    def _selectParent(self):
        self._clear()
        super_frame = tk.LabelFrame(self, text=msg.EX_SUPER_SKILL)
        if self.data.get("super_search"):
            var = self.data.get("super_search")
        else:
            self.data["super_search"] = var = tk.StringVar()
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

        skills = self.app.skills.getList(maxspec=2)
        l = [s[0] if s[1] == 1 else "    "+s[0] for s in skills]
        self.skill_list.insert(0, *l)

    def _searchSuper(self, var):
        search = var.get().lower()
        l = [s for s in self.loaded_skills if search in s.lower()]
        self.skill_list.delete(0, tk.END)
        self.skill_list.insert(0, *l)

    def _finalizeSkill(self):
        selected = self.skill_list.curselection()
        if len(selected) != 1:
            tkmb.showerror(msg.ERROR, msg.EX_NO_SUPER_SKILL, parent=self)
            return
        else:
            super_name = self.skill_list.get(selected[0]).strip()
            self.parent = self.app.skills.getSkill(super_name)
            parent_id = int(self.parent.get("id"))
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

            frame = tk.LabelFrame(self, text=msg.EX_NEW_SKILL)
            tk.Label(
                frame,
                text=self.data["name"].get(),
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
            id_frame = tk.Frame(frame)
            tk.Label(id_frame, text=msg.EX_ID).pack(side=tk.LEFT)
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

    def _addSkill(self):
        skill = et.Element("skill")
        skill.set("name", self.data["name"].get())
        skill.set("id", self.data["id"].get())
        skill.set("parent", self.parent.get("id"))
        skill.set("type", self.parent.get("type"))
        skill.set("spec", str(int(self.parent.get("spec")) + 1))
# HIER

        skills = self.app.module.expansion.find("skills")
        print(skills)
        skills.append(skill)
        self.app.module.updateSkills()


class TraitEditor(tk.Toplevel):
    def __init__(
        self,
        master=None,
        app=None,
        trait=None,
        expansion=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.app = app
        self.trait = trait
        self.expansion = expansion
    pass