import config
import tkinter as tk

msg = config.Messages()


class SkillInfo(tk.Toplevel):
    """ Displaying a window with additional information on a skill

    Args:
        app (Application): The main application instance
        name (str): the name of the skill
    """

    def __init__(self, app, name):
        tk.Toplevel.__init__(self)

        #  point to character and skilltree
        self.char = app.char
        self.all_skills = app.skills
        self.app = app
        self.skill = app.skills.getSkill(name)
        self.name = name

        self.overrideredirect(True)
        self.initialPosition()

        self.title_bar = tk.Frame(self)
        self.name_label = tk.Label(
            self.title_bar,
            text=name,
            font="Arial 12 bold"
        )
        self.name_label.pack(side=tk.LEFT)
        value = self.skill.get("value")
        self.value_label = tk.Label(
            self.title_bar,
            text=value,
            font="Arial 12 bold"
        )
        self.value_label.pack(side=tk.RIGHT, anchor=tk.E)
        self.title_bar.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=tk.NSEW
        )
        self.columnconfigure(0, weight=1000)

        self.canvas = tk.Canvas(
            self,
            width=200,
            height=200
        )
        self.canvas.grid(row=1, column=0)
        self.scrollbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL
        )
        self.scrollbar.grid(row=1, column=1, sticky=tk.NS)
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        self.showParent()

        self.showChildren()
        self.config(relief=tk.RIDGE, borderwidth=2)

        self.setScrollRegion()

        self.focus()
        self.bind("<Escape>", self.close)
        self.bind("<FocusOut>", self.close)

    def initialPosition(self):
        x, y = self.winfo_pointerxy()
        location = "+{x}+{y}".format(x=x-2, y=y-2)
        self.geometry(location)

    def setScrollRegion(self):
        x1, y1, x2, y2 = self.canvas.bbox(tk.ALL)
        x1 = 0
        x2 = 200
        self.canvas.config(scrollregion=(x1, y1, x2, y2))

    def showParent(self):
        parent_id = self.skill.get("parent")
        parent = self.all_skills.getSkillById(parent_id)
        spec = self.skill.get("spec")
        if spec == "1":
            info = msg.SI_SPEC1
        elif spec == "2":
            info = msg.SI_SPEC2
        elif spec == "3":
            info = msg.SI_SPEC3
        else:
            info = msg.SI_SPEC0

        info_label = tk.Label(
            self.canvas,
            text=info,
            font="Arial 9 italic"
        )

        y = 0
        self.canvas.create_window(100, y, window=info_label, anchor=tk.N)

        y += info_label.winfo_reqheight()

        if parent is not None:
            parent_name = parent.get("name")
            parent_label = tk.Label(self.canvas, text=parent_name)
            has_skill = self.char.getSkill(parent_name)
            if has_skill is None:
                parent_label.config(fg="#888888")

            self.canvas.create_window(100, y, window=parent_label, anchor=tk.N)

            y += parent_label.winfo_reqheight()

    def showChildren(self):

        y = self.canvas.bbox(tk.ALL)[3]
        id = self.skill.get("id")
        children = self.all_skills.getChildren(id)

        spec = self.skill.get("spec")
        if spec == "1":
            info = msg.SI_CHILD_SKILL
        elif spec == "2":
            info = msg.SI_CHILD_SPEC
        else:
            info = msg.SI_OTHER_SPEC

        label = tk.Label(
            self.canvas,
            text=info
        )
        self.canvas.create_window(
            100,
            y,
            window=label,
            anchor=tk.N
        )

        y += label.winfo_reqheight()

        for child in children:
            color = "#000000"
            child_name = child.get("name")
            if child_name == self.name:
                continue

            has_skill = self.char.getSkill(child_name)
            if has_skill is None:
                color = "#888888"

            label = tk.Label(
                self.canvas,
                text=child_name,
                fg=color
            )
            self.canvas.create_window(
                100,
                y,
                window=label,
                anchor=tk.N
            )

            y += label.winfo_reqheight()

    def close(self, event=None):
        self.app.open_windows["skill"] = 0
        self.destroy()

