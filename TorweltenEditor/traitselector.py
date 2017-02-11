import tkinter as tk
import config

msg = config.Messages()


class TraitSelector(tk.Toplevel):
    """ Creating a window for selecting character traits

    Args:
        app (Application) the main program instance
    """

    def __init__(self, app):
        tk.Toplevel.__init__(self, app)
        
        # point to character and traitstree
        self.char = app.char
        self.all_traits = app.traits
        self.app = app
        self.app.open_windows["trait"] = self

        # selected trait!
        self.trait = 0
        self.trait_cost = tk.StringVar()
        self.trait_cost.set("("+msg.XP+")")
        self.trait_cost.trace("w", self.xpCostChanged)
        self.trait_description = ""

        # build the window
        title = msg.TS_TITLE
        
        # the main window
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title(title)
        self.geometry("500x400")
        
        # the selection frame is used to display the search and listbox.
        self.left_frame = tk.Frame(self, width=250)
        self.search_frame = tk.Frame(self.left_frame)
        self.search = tk.StringVar()
        self.search.set(msg.TS_SEARCH_NAME)
        self.search_mode = "name"
        self.upper_search_frame = tk.Frame(self.search_frame)
        self.search_mode_name = tk.Button(
            self.upper_search_frame,
            text=msg.TS_NAME,
            relief=tk.SUNKEN,
            command=lambda:
                self.switchSearchMode("name")
        )
        self.search_mode_name.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.search_mode_cls = tk.Button(
            self.upper_search_frame,
            text=msg.TS_CLASS,
            command=lambda:
                self.switchSearchMode("cls")
        )
        self.search_mode_cls.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.search_mode_grp = tk.Button(
            self.upper_search_frame,
            text=msg.TS_GROUP,
            command=lambda:
                self.switchSearchMode("grp")
        )
        self.search_mode_grp.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.upper_search_frame.pack(fill=tk.X, expand=1)
        self.lower_search_frame = tk.Frame(self.search_frame)
        self.search_box = tk.Entry(
            self.lower_search_frame,
            textvariable=self.search)
        self.search_box.bind("<Control-a>", self.searchSelectAll)
        self.search_box.bind("<Return>", lambda event: self.searchTraits())
        self.search_box.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.search_button = tk.Button(
            self.lower_search_frame,
            text=msg.TS_SEARCH,
            command=self.searchTraits
        )
        self.search_button.pack(side=tk.RIGHT)
        self.lower_search_frame.pack(fill=tk.X, expand=1)
        self.search_frame.pack(fill=tk.X)
        self.select_frame = tk.Frame(self.left_frame)
        self.scrollbar_select = tk.Scrollbar(
            self.select_frame,
            orient=tk.VERTICAL
        )
        self.list_box = tk.Listbox(self.select_frame)
        self.list_box.config(
            yscrollcommand=self.scrollbar_select.set,
            height=20,
            width=30)
        self.scrollbar_select.config(command=self.list_box.yview)
        self.list_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.list_box.bind("<<ListboxSelect>>", self.displayTraitInfo)
        self.scrollbar_select.pack(side=tk.RIGHT, fill=tk.Y, expand=1)
        self.select_frame.pack(fill=tk.Y, expand=1)
        self.left_frame.pack(fill=tk.Y, side=tk.LEFT, expand=1)
        
        # the info frame displays the information about the selected trait.
        self.info_frame = tk.Frame(self, width=300)
        self.info_title_frame = tk.Frame(self.info_frame)
        self.info_xp = tk.Label(
            self.info_title_frame,
            textvariable=self.trait_cost,
            font="Arial 12 bold"
        )
        self.info_xp.pack(side=tk.RIGHT)
        self.info_title = tk.Label(
            self.info_title_frame,
            text=msg.TS_TRAIT,
            font="Arial 12 bold",
            justify=tk.LEFT
        )
        self.info_title.pack(fill=tk.X, side=tk.LEFT)
        self.info_title_frame.pack(fill=tk.X)
        self.info_subtrait_container = tk.Frame(self.info_frame)
        self.info_subtrait = tk.Frame(self.info_subtrait_container)
        self.info_subtrait.pack(fill=tk.X)
        self.info_subtrait_container.pack(fill=tk.X)
        self.info_subtrait_widgets = {}
        self.info_subtrait_vars = {}
        self.info_subtrait_tcl = {}
        self.info_description_frame = tk.Frame(self.info_frame)
        self.info_description = tk.Text(self.info_description_frame)
        self.info_description.bind("<KeyRelease>", self.updateDescription)
        self.info_description.insert(tk.END, msg.TS_DESCRIPTION)
        self.info_description.config(font="Arial 10", wrap=tk.WORD)
        self.info_scrollbar = tk.Scrollbar(
            self.info_description_frame,
            orient=tk.VERTICAL
        )
        self.info_description.config(yscrollcommand=self.info_scrollbar.set)
        self.info_scrollbar.config(command=self.info_description.yview)
        self.info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_description.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # the submit button
        self.submit = tk.Button(
            self.info_frame,
            text=msg.TS_ADD_TRAIT,
            command=self.addTrait)
        self.submit.pack(side=tk.BOTTOM, fill=tk.X)
        self.info_description_frame.pack(fill=tk.BOTH)

        self.info_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        
        self.listTraits()
        self.focus()
    
    def listTraits(self, search=False):
        traits = self.all_traits.getList()
        # clear the listbox
        self.list_box.delete(0, tk.END)

        cur_traits = [trait.get("name") for trait in self.char.getTraits()]
        for trait in traits:
            if search is False:
                self.list_box.insert(tk.END, trait[0])
            if search is True:
                selector = 0
                if self.search_mode == "name":
                    selector = 0
                if self.search_mode == "cls":
                    selector = 1
                if self.search_mode == "grp":
                    selector = 2
                
                search_term = self.search.get()
                if trait[selector]:
                    if search_term.lower() in trait[selector].lower():
                        self.list_box.insert(tk.END, trait[0])

    # the player selects a trait
    def displayTraitInfo(self, event):
        self.info_subtrait_vars = {}
        self.info_subtrait_tcl = {}
        self.trait_description = ""
        selection = event.widget.curselection()
        selected = ""
        for item in selection:
            selected = self.list_box.get(item)
        
        self.trait = self.all_traits.getTrait(selected)
        trait_name = self.trait.get("name")
        trait_cost = self.trait.get("xp")
        self.trait_cost.set("("+trait_cost+")")

        self.info_title.config(text=trait_name)

        self.info_description.delete(1.0, tk.END)
        self.setDescription()

        # destroy the subtrait frame and recreate it
        self.info_subtrait.destroy()
        self.info_subtrait = tk.Frame(self.info_subtrait_container)
        self.info_subtrait.pack(fill=tk.X)

        # check if the trait has a specification: 
        specification = self.trait.find("specification")
        if specification is not None:
            specification_frame = tk.Frame(self.info_subtrait)
            specification_label_text = specification.get("name")
            specification_label = tk.Label(
                specification_frame,
                text=specification_label_text+": ")
            specification_label.pack(side=tk.LEFT)
            # create a stringvar
            spec_var = tk.StringVar()
            self.info_subtrait_vars["spec"] = spec_var
            spec_var.set("")
            spec_var.trace("w", self.variableChanged)
            # bind the tcl_name of the variable to the variable
            self.info_subtrait_tcl[str(spec_var)] = "spec"
            specification_entry = tk.Entry(
                specification_frame,
                textvariable=self.info_subtrait_vars["spec"]
            )
            self.info_subtrait_widgets["spec"] = specification_entry
            specification_entry.pack(side=tk.LEFT, fill=tk.X)
            specification_frame.pack(fill=tk.X)
        
        # check for a rank tag:
        ranks = self.trait.findall("rank")
        if ranks is not None:
            for rank in ranks:
                rank_name = rank.get("name")
                rank_id = rank.get("id")
                xp_factor = int(rank.get("xp"))
                min_rank = int(rank.get("min", "1"))
                max_rank = int(rank.get("max", "10"))
                rank_frame = tk.Frame(self.info_subtrait)
                rank_label = tk.Label(rank_frame, text=rank_name)
                rank_label.pack(side=tk.LEFT)
                var = tk.StringVar()
                self.info_subtrait_vars["rank"+"_"+rank_id] = var
                var.set(min_rank)
                var.trace("w", self.variableChanged)
                # bind the label to the tcl_name
                self.info_subtrait_tcl[str(
                    self.info_subtrait_vars["rank_"+rank_id]
                )] = "rank_"+rank_id
                spinbox = tk.Spinbox(
                    rank_frame,
                    textvariable=var,
                    from_=min_rank,
                    to=max_rank
                )
                self.info_subtrait_widgets["rank"+rank_id] = spinbox
                spinbox.pack(side=tk.RIGHT)
                rank_frame.pack()

        # check if there are variables
        variables = self.trait.findall("variable")
        if variables is not None:
            rownum = 0
            variable_frame = tk.Frame(self.info_subtrait)
            for variable in variables:
                variable_label_text = variable.get("name")
                variable_id = variable.get("id")
                variable_values_string = variable.get("values")
                variable_values = variable_values_string.split(",")
                variable_label = tk.Label(
                    variable_frame,
                    text=variable_label_text)
                variable_label.grid(row=rownum, column=0)
                # create a string_var for the variable
                var = tk.StringVar()
                self.info_subtrait_vars["var"+"_"+variable_id] = var
                var.trace("w", self.variableChanged)
                # bind the label to the tcl_name

                self.info_subtrait_tcl[str(var)] = "var"+"_"+variable_id
                spinbox = tk.Spinbox(
                    variable_frame,
                    textvariable=var,
                    values=variable_values)
                self.info_subtrait_widgets["var"+"_"+variable_id] = spinbox
                spinbox.grid(row=rownum, column=1)
                rownum += 1
            variable_frame.pack()
    
    def updateDescription(self, event):
        self.trait_description = self.info_description.get("0.0", tk.END)

    def xpCostChanged(self, *args):
        xp_string = self.trait_cost.get()
        xp_string = xp_string[1:-1]
        try:
            xp = int(xp_string)
            if xp == 0:
                self.info_xp.config(fg=config.Colors.BLACK)
                self.submit.config(state=tk.DISABLED)
            if xp < 0:
                self.info_xp.config(fg=config.Colors.DARK_RED)
                self.submit.config(state=tk.NORMAL)
            if xp > 0:
                self.info_xp.config(fg=config.Colors.DARK_GREEN)
                self.submit.config(state=tk.NORMAL)
        except ValueError:
            pass
        
    # one of the variables was changed ...
    def variableChanged(self, *args):
        trait_cost = 0

        # retrieve the ranks and calculate their cost!
        ranks = self.trait.findall("rank")
        if len(ranks) > 0:
            for rank in ranks:
                xp_factor = int(rank.get("xp"))
                min_rank = int(rank.get("min", "1"))
                max_rank = int(rank.get("max", "10"))
                rank_id = rank.get("id")
                
                # it is possible that the variable hast not yet been created!!
                try:
                    selected = self.info_subtrait_vars["rank_"+rank_id].get()
                    operand = rank.get("operand")
                    if operand is None:
                        operand = "add"
                    try: 
                        selected = int(selected)
                        if selected > max_rank:
                            selected = max_rank
                        if selected < min_rank:
                            selected = min_rank
                    except ValueError:
                        selected = min

                    self.info_subtrait_vars["rank_"+rank_id].set(selected)
                    if operand == "add":
                        trait_cost += selected * xp_factor

                    if operand == "multiply" and trait_cost == 0:
                        trait_cost = (selected * xp_factor)

                    if operand == "multiply" and trait_cost != 0:
                        trait_cost *= (selected * xp_factor)

                except KeyError: 
                    trait_cost = 0
        
        # retrieve the variables: 
        variables = self.trait.findall("variable")
        if len(variables) > 0:        
            for variable in variables:
                # create the xp cost dict
                xp_list = variable.get("xp")
                values_list = variable.get("values")
                xp = xp_list.split(",")
                values = values_list.split(",")
                xp_dict = {}
                i = 0
                for value in values:
                    xp_dict[value] = float(xp[i])
                    i += 1

                # get the id of the variable
                id = variable.get("id")
                # retrieve the StringVar()
                # we have to try because the variables
                # have not yet all been created
                try:
                    selected = self.info_subtrait_vars["var_"+id].get()
                # get the operand and modify the xp value ...
                    operand = variable.get("factor", "add")
                    if operand == "add":
                        trait_cost = trait_cost + xp_dict[selected]
                    elif operand == "multiply":
                        if trait_cost == 0:
                            trait_cost = xp_dict[selected]
                        else:
                            trait_cost = trait_cost * xp_dict[selected]
                except KeyError:
                    trait_cost = 0

        # rounding mathematically and making sure the value is at least +-1
        trait_cost = round(trait_cost)
        if 0 < trait_cost < 1:
            trait_cost = 1
        if -1 < trait_cost < 0:
            trait_cost = -1
        
        # check if the specification is not empty
        try: 
            specification = self.info_subtrait_vars["spec"].get()
            if specification == "":
                trait_cost = 0
        except KeyError:
            pass

        # update the xp widget
        self.trait_cost.set("(" + str(int(trait_cost)) + ")")

        if trait_cost < 0:
            self.info_xp.config(fg=config.Colors.DARK_RED)
        elif trait_cost == 0:
            self.info_xp.config(fg=config.Colors.BLACK)
        else:
            self.info_xp.config(fg=config.Colors.DARK_GREEN)

    # add the text    
    def setDescription(self):
        text_fragments = self.trait.findall(".//description")
        for fragment in text_fragments:
            self.info_description.insert(tk.END, fragment.text)
    
    def switchSearchMode(self, mode):
        if mode != self.search_mode:
            self.search_mode = mode
            if mode == "name":
                self.search_mode_name.config(relief=tk.SUNKEN)
                self.search_mode_cls.config(relief=tk.RAISED)
                self.search_mode_grp.config(relief=tk.RAISED)
                self.search_box.pack_forget()
                self.search_box = tk.Entry(
                    self.lower_search_frame,
                    textvariable=self.search
                )
                self.search_box.pack(fill=tk.BOTH)
                self.search_box.bind("<Control-a>", self.searchSelectAll)
                self.search_box.bind(
                    "<Return>",
                    lambda event:
                        self.searchTraits()
                )
                self.search.set(msg.TS_SEARCH_NAME)
            if mode == "cls":
                self.search_mode_name.config(relief=tk.RAISED)
                self.search_mode_cls.config(relief=tk.SUNKEN)
                self.search_mode_grp.config(relief=tk.RAISED)

                self.search_box.pack_forget()
                self.search_box = tk.Spinbox(
                    self.lower_search_frame,
                    textvariable=self.search
                )
                self.search_box.pack(fill=tk.BOTH)
                self.search_box.bind(
                    "<Return>",
                    lambda event:
                        self.searchTraits()
                )

                traits = self.all_traits.getList()
                trait_set = set()
                for trait in traits:
                    if trait[1]:
                        trait_set.add(trait[1])
                trait_list = list(trait_set)
                self.search_box.config(values=trait_list)
                self.search.set(msg.TS_JUST_SCROLL)
                
            if mode == "grp":
                self.search_mode_name.config(relief=tk.RAISED)
                self.search_mode_cls.config(relief=tk.RAISED)
                self.search_mode_grp.config(relief=tk.SUNKEN)

                self.search_box.pack_forget()
                self.search_box = tk.Spinbox(
                    self.lower_search_frame,
                    textvariable=self.search
                )
                self.search_box.pack(fill=tk.BOTH)
                self.search_box.bind(
                    "<Return>",
                    lambda event:
                    self.searchTraits()
                )

                traits = self.all_traits.getList()
                trait_set = set()
                for trait in traits:
                    if trait[2]:
                        trait_set.add(trait[2])
                trait_list = list(trait_set)
                self.search_box.config(values=trait_list)
                self.search.set(msg.TS_JUST_SCROLL)

    def searchTraits(self):
        self.listTraits(True)

    # player presses the add trait button
    def addTrait(self):
        self.char.addTrait(
            self.trait,
            self.info_subtrait_vars,
            self.trait_cost,
            self.trait_description
        )

        # finally close the window
        self.app.updateTraitList()
        self.close()

    @staticmethod
    def searchSelectAll(event):
        widget = event.widget
        widget.select_range(0, tk.END)
        return "break"
    
    def close(self):
        self.destroy()
        self.app.open_windows["trait"] = 0
