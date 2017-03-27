import tkinter as tk
import config

# Display additional information about selected traits ... # #


class TraitInfo(tk.Toplevel):
    def __init__(self, app, event):
        tk.Toplevel.__init__(self, app)
        self.app = app
        self.char = app.char
        self.traits = app.traits

        x = event.x_root
        y = event.y_root
        geometry = "+"+str(x)+"+"+str(y)
        self.geometry(geometry)

        self.overrideredirect(True)

        # for positioning stuff on the widget
        self.y = 0

        # get the information ...
        self.char_trait = self.getCharTrait(event)
        self.trait_name = self.char_trait.get("name")
        self.specification = self.char_trait.findall("./specification")
        self.ranks = self.char_trait.findall("./rank")
        self.variables = self.char_trait.findall("./variable")
        self.trait = self.traits.getTrait(self.trait_name)
        self.id = self.char_trait.get("id")

        self.trait_xp = self.char_trait.get("xp")

        self.config(relief=tk.RIDGE, borderwidth=2)
        # preparing the canvas
        self.canvas = tk.Canvas(self, width=300, height=200)
        self.canvas.pack(side=tk.LEFT)
        self.scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.scroll.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scroll.set)

        # render content
        self.drawTitle()
        self.drawSpecification()
        self.drawRanks()
        self.drawVariables()
        self.drawDescription()
        self.finalize()

    # retrieve the character trait based on the id passed as text_tag
    def getCharTrait(self, event):
        text = event.widget
        index = text.index(tk.CURRENT)
        tags = text.tag_names(index)
        trait = self.char.getTraitByID(tags[0])
        return trait

    def drawTitle(self):
        """ Renders the title of the window """

        x = 5
        title_width = 250
        if self.char.getEditMode() == "generation":
            remove_button = tk.Button(
                self.canvas,
                text="Entfernen",
                command=self.removeTrait
            )
            self.canvas.create_window(
                0,
                0,
                window=remove_button,
                anchor=tk.NW
            )
            x += remove_button.winfo_reqwidth() + 5
            title_width -= x

        title = tk.Label(
            self.canvas,
            font="Arial 12 bold",
            text=self.trait_name,
            wraplength=title_width,
            justify=tk.LEFT
        )

        xp = tk.Label(
            self.canvas,
            font="Arial 12 bold",
            text="("+self.trait_xp+")",
            justify=tk.RIGHT
        )
        if int(self.trait_xp) > 0:
            xp.config(foreground=config.Colors.DARK_GREEN)
        else:
            xp.config(foreground=config.Colors.DARK_RED)

        self.canvas.create_window(
            x,
            0,
            window=title,
            width=title_width,
            anchor=tk.NW
        )
        self.y += title.winfo_reqheight()

        self.canvas.create_window(
            298,
            0,
            window=xp,
            anchor=tk.NE
        )

    def drawSpecification(self):
        """ Looks for specification and renders it """

        for specification in self.specification:
            text = "{name}: {value}".format(
                name=specification.get("name"),
                value=specification.get("value")
            )
            self.drawText(text, font="Arial 10 bold")

    def drawDescription(self):
        """ Finds the description and draws it """

        description = self.char_trait.find("description")
        if description is None:
            description = self.trait.find("./description")
        if description.text:
            self.drawText(description.text)

    def drawRanks(self):
        """ Looks for ranks and renders them """
        for rank in self.ranks:
            rank_name = rank.get("name")
            rank_value = rank.get("value")
            text = "{rank}: {value}".format(
                rank=rank_name,
                value=rank_value
            )
            self.drawText(text, font="Arial 10 bold")

    def drawVariables(self):
        """ Go through variables and add them (including description) """

        for variable in self.variables:
            var_name = variable.get("name")
            var_value = variable.get("value")
            text = "{variable}: {value}".format(
                variable=var_name,
                value=var_value
            )
            self.drawText(text, font="Arial 10 bold")

            search = "./description[@value='"+var_value+"']"
            description = variable.find(search)
            if description is not None:
                if description.text:
                    self.drawText(description.text)

    def drawText(self, text, font="Arial 9"):
        """ Helper method to draw text to the canvas

        Args:
            text (str): the text to draw
            font (str): the font used
        """

        label = tk.Label(
            self.canvas,
            text=text,
            font=font,
            wrap=290,
            justify=tk.LEFT
        )
        self.canvas.create_window(
            5,
            self.y,
            width=290,
            window=label,
            anchor=tk.NW,
        )
        self.y += label.winfo_reqheight()

    def updateTraitRank(self, rank_id, delta):
        rank_tag = self.trait.find("./rank[@id='"+rank_id+"']")

    def removeTrait(self):
        """ Removing the trait """

        self.char.removeTraitByID(self.id)
        self.destroy()
        self.app.updateTraitList()

    def finalize(self):
        """ Called at the end of layout to set scroll area"""

        x1, y1, x2, y2 = self.canvas.bbox(tk.ALL)
        x1 = 0
        x2 = 300
        self.canvas.config(scrollregion=(x1, y1, x2, y2))
        self.focus()
        self.bind("<Escape>", self.close)
        self.bind("<FocusOut>", self.close)

    def close(self, event=None):
        self.destroy()
