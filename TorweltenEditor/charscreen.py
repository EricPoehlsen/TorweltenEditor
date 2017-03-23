import config
from traitselector import TraitSelector
from traitinfo import TraitInfo
from skillselector import SkillSelector
from skillinfo import SkillInfo
from PIL import ImageTk,Image,PngImagePlugin
from tooltip import ToolTip

import tkinter as tk

msg = config.Messages()


class CharScreen(tk.Frame):
    """ The CharScreen displays the character on the main window

    Args:
        main (tk.Frame): the parent frame in which to display
        app (Application): the main application
    """

    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        # localize data ... 
        # create the character instance # #
        self.app = app
        self.char = app.char
        self.skills = app.skills
        self.traits = app.traits
        self.itemlist = app.itemlist

        # stuff that needs to be available across some functions
        self.global_vars = dict()

        # defining subwindows to track them!
        self.open_windows = app.open_windows

        self.widgets = {}

        # from here on we are building the screen layout ...

        # column 1 ...
        self.frame_1 = frame_1 = tk.Frame(self)

        # starting with the attribute frame ...
        attr_frame = tk.Frame(frame_1)
        attr_list = self.char.ATTRIB_LIST

        for attr in attr_list:
            frame = tk.LabelFrame(attr_frame, text=attr.upper())
            # initiate the IntVars and bind their tcl names to the attributes
            attrib_values = self.char.attrib_values
            attrib_values[attr] = tk.IntVar()
            attrib_values[attr].set(self.char.getAttributeValue(attr))
            
            # in generation mode we have spinboxes ...             
            if self.char.getEditMode() == "generation":
                self.char.attrib_trace[str(attrib_values[attr])] = attr

                self.widgets[attr] = tk.Spinbox(
                    frame, 
                    from_=0, 
                    to=9, 
                    textvariable=attrib_values[attr], 
                    font="Arial 12 bold", 
                    width=3
                )
                self.widgets[attr].pack()
                self.char.widgets = self.widgets
                self.char.attrib_values[attr].trace(
                    "w",
                    self.char.attributeChange
                )

            # in edit mode there are buttons and labels
            if self.char.getEditMode() == "edit":
                value_field = tk.Label(
                    frame, 
                    textvariable=attrib_values[attr], 
                    font="Arial 12 bold",
                    width=3
                )
                value_field.pack(side=tk.LEFT)
                self.widgets[attr+"_inc"] = tk.Button(
                    frame, 
                    text="+",
                    command=lambda attr=attr:
                        self.increaseAttribute(attr)
                )
                self.widgets[attr+"_inc"].pack(side=tk.RIGHT)
            
            # in view mode there is only a label ...
            if self.char.getEditMode() == "view":
                value_field = tk.Label(
                    frame,
                    textvariable=attrib_values[attr], 
                    font="Arial 12 bold",
                    width=3
                )
                value_field.pack()

            frame.pack()
        attr_frame.pack(anchor=tk.N)
        
        # this displays the characters XP
        xp_frame = tk.LabelFrame(frame_1, text=msg.XP)
        xp_avail = tk.Label(
            xp_frame,
            textvariable=self.char.xp_avail
        )
        self.char.xp_avail.set(self.char.getAvailableXP())
        xp_avail.pack(side=tk.LEFT)
        xp_total_text = " / " + str(self.char.getTotalXP())
        self.xp_total = tk.Label(xp_frame, text=xp_total_text)
        self.xp_total.pack(side=tk.LEFT)
        xp_frame.pack()
        
        frame_1.pack(side=tk.LEFT, anchor=tk.N)
        
        # this makes the second block 
        frame_2 = tk.Frame(self)
        
        # beginning with the data frame 
        data_frame = tk.LabelFrame(
            frame_2,
            text=msg.CS_BASE_DATA,
            font="Arial 10 bold"
        )

        data_list = [
            ['name', msg.NAME, 0, 0, 4],
            ['species', msg.SPECIES, 1, 0, 4],
            ['origin', msg.ORIGIN, 2, 0, 4],
            ['concept', msg.CONCEPT, 3, 0, 4],
            ['player', msg.PLAYER, 4, 0, 4],
            ['height', msg.HEIGHT, 5, 0, 1],
            ['weight', msg.WEIGHT, 5, 1, 1],
            ['age', msg.AGE, 5, 2, 1],
            ['gender', msg.GENDER, 5, 3, 1],
            ['hair', msg.HAIR, 6, 0, 1],
            ['eyes', msg.EYES, 6, 1, 1],
            ['skin', msg.SKIN_COLOR, 6, 2, 1],
            ['skintype', msg.SKIN_TYPE, 6, 3, 1]
        ]
        for data in data_list:
            frame = tk.LabelFrame(data_frame, text=data[1])
            # creating a StringVar() and linking the tcl name
            value_var = tk.StringVar()
            self.char.data_values[data[0]] = value_var
            self.char.data_trace[str(value_var)] = data[0]

            # retrieve already stored data from character
            stored_value = self.char.getData(data[0])
            
            if stored_value:
                value_var.set(stored_value)

            width = 10 * data[4]
            entry = tk.Entry(
                frame, 
                textvariable=value_var,
                width=width
            )
            entry.bind("<FocusOut>", self.dataUpdated)
            entry.pack(fill=tk.X, expand=1)
            frame.grid(
                row=data[2],
                column=data[3],
                columnspan=data[4],
                sticky="WE"
            )
        
        for row in range(7):
            data_frame.rowconfigure(row, weight=1)
        for col in range(4):
            data_frame.columnconfigure(col, weight=1)
        data_frame.pack(fill=tk.BOTH, anchor=tk.N, expand=1)

        # within this frame will be the character traits
        traits_frame = tk.LabelFrame(
            frame_2,
            text=msg.CS_TRAITS,
            font="Arial 10 bold"
        )
        self.traits_text = tk.Text(
            traits_frame, 
            bg="#dddddd", 
            font="Arial 10",
            wrap=tk.WORD,
            height=10,
            width=10
        )
        self.updateTraitList()

        # finally pack the field and disable it for editing
        self.traits_text.pack(fill=tk.BOTH, expand=1)
        traits_frame.pack(fill=tk.BOTH, expand=1)

        new_traits_button = tk.Button(
            traits_frame, 
            text=msg.CS_ADD_TRAIT, 
            command=self.showTraitWindow
        )
        new_traits_button.pack(fill=tk.X)
        traits_frame.pack(fill=tk.BOTH, expand=1)

        # TODO (Eric): This is just a text for the tooltip
        new_traits_button.bind("<Enter>", self.showTooltip)

        frame_2.pack(side=tk.LEFT, anchor=tk.N, fill=tk.Y, expand=1)

        # this frame holds the character skills ... 
        frame_3 = tk.Frame(self)

        # active skills ...
        self.active_skill_frame = tk.LabelFrame(
            frame_3, 
            text=msg.CS_ACTIVE_SKILLS, 
            font="Arial 10 bold"
        )
        self.active_skill_canvas = tk.Canvas(
            self.active_skill_frame,
            width=190,
            height=500
        )
        self.active_skill_canvas.pack(side=tk.LEFT)
        self.active_skill_scroll = tk.Scrollbar(
            self.active_skill_frame,
            orient=tk.VERTICAL
        )
        self.active_skill_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.active_skill_scroll.config(
            command=self.active_skill_canvas.yview
        )
        self.active_skill_canvas.config(
            yscrollcommand=self.active_skill_scroll.set
        )

        # passive skills
        self.passive_skill_frame = tk.LabelFrame(
            frame_3, 
            text=msg.CS_PASSIVE_SKILLS,
            font="Arial 10 bold"
        )
        self.passive_skill_canvas = tk.Canvas(
            self.passive_skill_frame,
            width=190,
            height=500
        )
        self.passive_skill_canvas.pack(side=tk.LEFT)
        self.passive_skill_scroll = tk.Scrollbar(
            self.passive_skill_frame,
            orient=tk.VERTICAL
        )
        self.passive_skill_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.passive_skill_scroll.config(
            command=self.passive_skill_canvas.yview
        )
        self.passive_skill_canvas.config(
            yscrollcommand=self.passive_skill_scroll.set
        )

        # initialize the list and place it on screen ...
        self.updateSkillList()
        self.active_skill_frame.grid(row=0, column=0, sticky="nsew")
        self.passive_skill_frame.grid(row=0, column=1, sticky="nsew")
        
        # and a button to add skills
        new_skill_button = tk.Button(
            frame_3, 
            text=msg.CS_ADD_SKILLS, 
            command=self.showSkillWindow
        )
        new_skill_button.grid(row=1, column=0, columnspan=2, sticky="nsew")

        frame_3.rowconfigure(0, weight=100)
        frame_3.pack(side=tk.LEFT, anchor=tk.N, fill=tk.BOTH)

    def increaseAttribute(self, attr):
        """ Passing on a click to the 'increase attribute' button """

        self.char.increaseAttribute(attr)

    def increaseSkill(self, skill_name, canvas):
        """ Handling a click the 'increase skill' button

        As in edit mode the skill value is displayed as a canvas text
        object it is necessary to access and modify it if the skill is
        changed .

        Args:
            skill_name (str): name of skill
            canvas (Canvas): the canvas the skill is shown on
        """

        self.char.increaseSkill(skill_name)

        # update text in edit mode ... 
        if self.char.getEditMode() == "edit":
            new_value = self.char.skill_values[skill_name].get()
            
            id = self.widgets[skill_name+"_txt"]
            canvas.itemconfig(id, text=new_value)

    def dataUpdated(self, event):
        """ Passing modified character data to the character """

        var_name = event.widget.cget("textvariable")
        data_name = self.char.data_trace[var_name]
        data_value = self.char.data_values[data_name].get()
        self.char.updateData(data_name, data_value)

    def updateTraitList(self):
        """ Fill the traits text widget with content. """

        character_traits = self.char.getTraits()
        self.traits_text.config(state=tk.NORMAL)
        self.traits_text.delete("1.0", tk.END)

        tag_id = 0
        for trait in character_traits:
            # insert a comma separator after the last trait
            if self.traits_text.index(tk.CURRENT) != "1.0":
                self.traits_text.insert(tk.CURRENT, ", ")

            # get the name
            trait_name = trait.get("name")
            trait_id = trait.get("id")
            # get the specification if there is one
            trait_specification = ""
            selected = trait.find("selected")

            specification = trait.find("specification")
            if specification is not None:
                value = specification.get("value")
                trait_specification = " ["+value+"]"
            
            # get the xp
            trait_xp = trait.get("xp")
            
            # insert the name of the trait and the specification.
            # Bind text to the TraitInfoBaloon
            index_start = self.traits_text.index(tk.CURRENT)
            self.traits_text.insert(tk.END, trait_name)
            self.traits_text.insert(tk.END, trait_specification)
            index_end = self.traits_text.index(tk.CURRENT)
            self.traits_text.tag_add(trait_id, index_start, index_end)
            self.traits_text.tag_bind(
                trait_id,
                "<Button-1>",
                lambda event:
                    self.showTraitInfo(event)
            )
            self.traits_text.tag_config(trait_id, foreground="#000000")

            # insert the xp of the trait and color it accordingly
            index_start = self.traits_text.index(tk.CURRENT)
            self.traits_text.insert(tk.END, " ("+trait_xp+")")
            index_end = self.traits_text.index(tk.CURRENT)
            self.traits_text.tag_add(
                "tag"+str(tag_id),
                index_start,
                index_end
            )
            if int(trait_xp) < 0:
                self.traits_text.tag_config(
                    "tag"+str(tag_id),
                    foreground=config.Colors.DARK_RED
                )
            else:
                self.traits_text.tag_config(
                    "tag"+str(tag_id),
                    foreground=config.Colors.DARK_GREEN
                )
            
            tag_id += 1
        self.traits_text.config(state=tk.DISABLED)

    def updateSkillList(self):
        """ Render the contents of the skill lists """

        # retrieve edit mode once ... 
        edit_mode = self.char.getEditMode()

        # clear the canvas ... 
        self.active_skill_canvas.delete(tk.ALL)
        self.passive_skill_canvas.delete(tk.ALL)

        # sort the skills         
        self.char.sortSkills()

        # add entries to the lists ...
        active_count = 0
        passive_count = 0
        skills = self.char.getSkills()
        for skill in skills:

            # decide which side this skill goes to ...
            skill_type = skill.get("type")
            if skill_type == "active":
                canvas = self.active_skill_canvas
                active_count += 1
                y_pos = (active_count - 1)

            else:
                canvas = self.passive_skill_canvas
                passive_count += 1
                y_pos = (passive_count - 1)

            # get skill name and specialization - set font accordingly
            skill_text = skill.get("name")
            skill_font = ""
            skill_spec = int(skill.get("spec", "2"))
            if skill_spec == 1:
                skill_font = "Arial 10 bold"
            elif skill_spec == 2:
                skill_font = "Arial 10"
            elif skill_spec == 3:
                skill_font = "Arial 10 italic"

            # creating a IntVar() and linking tcl variable name to skill_name
            value_var = self.char.skill_values[skill_text] = tk.IntVar()
            self.char.skill_trace[str(value_var)] = skill_text
            
            # retrieve the current value 
            skill_value = int(skill.get("value"))
            value_var.set(skill_value)
            
            # how to display the value (spinbox / value+button / only value)
            if edit_mode == "generation":
                # adding a trace to the variable
                value_var.trace("w", self.char.skillChange)

            # use a spinbox to move skill up and down
            value_spinner = tk.Spinbox(
                canvas, 
                from_=0, 
                to=3, 
                textvariable=value_var,
                width=2, 
                font="Arial 10 bold"
                )
            # or a button just to increase skill
            value_button = self.widgets[skill_text+"_inc"] = tk.Button(
                canvas,
                text="+",
                command=lambda canvas=canvas, skill_text=skill_text:
                    self.increaseSkill(skill_text, canvas)
            )
            value_text = self.char.skill_values[skill_text].get()
 
            # render the line to the canvas
            height = 24
            # background
            if y_pos % 2 == 0:
                local_y = y_pos * height - 2
                canvas.create_rectangle(
                    0,                  # x1
                    local_y,            # y1
                    190,                # x2
                    local_y + height,   # y2
                    fill="#ddddff",
                    outline="#ddddff"
                )
            # name
            text = canvas.create_text(
                2,                  # x
                y_pos*height + 2,   # y
                anchor=tk.NW,
                text=skill_text,
                font=skill_font
            )
            canvas.tag_bind(
                text,
                "<Button-1>",
                lambda event, name=skill_text:
                    self.showSkillInfo(name)
            )

            # value
            if edit_mode == "generation": 
                canvas.create_window(
                    190,            # x
                    y_pos*height,   # y
                    anchor=tk.NE,
                    window=value_spinner
                )
            elif edit_mode == "edit":
                canvas.create_window(
                    190,            # x
                    y_pos*height,   # y
                    anchor=tk.NE,
                    window=value_button
                )
                self.widgets[skill_text+"_txt"] = canvas.create_text(
                    170,            # x
                    y_pos*height,   # y
                    anchor=tk.NE,
                    text=value_text,
                    font="Arial 10 bold"
                )
            else:
                canvas.create_text(
                    190,            # x
                    y_pos*height,   # y^
                    anchor=tk.NE,
                    text=value_text,
                    font="Arial 10 bold")

        # set scroll regions based on content 
        self.active_skill_canvas.config(
            scrollregion=self.active_skill_canvas.bbox("all")
        )
        self.passive_skill_canvas.config(
            scrollregion=self.passive_skill_canvas.bbox("all")
        )

    def showSkillWindow(self):
        """ Opening a window to add character skills"""

        if self.open_windows["skill"] != 0:
            self.open_windows["skill"].focus()
        else:
            # first check if the character may be edited
            edit_mode = self.char.getEditMode()
            if edit_mode in ["generation", "edit"]:
                SkillSelector(self)

    def showTraitWindow(self):
        """ Opening a window to add character traits """

        if self.open_windows["trait"] != 0:
            self.open_windows["trait"].trait_editor.focus()
        else:
            # first check if the character may be edited
            edit_mode = self.char.getEditMode()
            if edit_mode in ["generation", "edit"]:
                # open the skill selector
                TraitSelector(self)

    def showTraitInfo(self, event):
        window = TraitInfo(self, event)

    def showSkillInfo(self, name):
        window = SkillInfo(self, name)

    def showTooltip(self, event):
        widget = event.widget
        buttontext = widget.cget("text")

        infos = {
            msg.CS_ADD_TRAIT: msg.TT_ADD_TRAITS
        }

        ToolTip(
            self.winfo_toplevel(),
            event=event,
            message=infos[buttontext]
        )
