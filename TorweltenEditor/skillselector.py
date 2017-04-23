""" This module is responsible for the skill selection window """

import config
import tk_ as tk
import re
from PIL import ImageTk
from tooltip import ToolTip

msg = config.Messages()

# this class creates a SkillSelectionWindow        


class SkillSelector(tk.Toplevel):
    def __init__(self, app):
        tk.Toplevel.__init__(self, app)
        #  point to character and skilltree
        self.char = app.char
        self.all_skills = app.skills
        self.app = app
        self.app.open_windows["skill"] = self

        self.minspec = 1
        self.maxspec = 3
        self.origin = ""
        self.complete_list = [skill[0] for skill in self.all_skills.getList()]

        # icons:
        self.unsel_icon = ImageTk.PhotoImage(file="img/unsel.png")
        self.sel_icon = ImageTk.PhotoImage(file="img/sel.png")


        #  build the window
        if self.char.getEditMode == "generation":
            self.title(msg.SS_ADD_REMOVE_SKILLS)
        else:
            self.title(msg.SS_ADD_SKILLS)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.search_frame = tk.Frame(self)
        self.search = tk.StringVar()
        self.search_gf = tk.Button(
            self.search_frame,
            width=3,
            text=msg.SS_BASE,
            command=self.toggleMinSpec
        )
        self.search_gf.config(relief=tk.SUNKEN)
        ToolTip(self.search_gf, msg.SS_TT_SHOW_BASE)
        self.search_gf.pack(side=tk.LEFT)
        self.search_sp = tk.Button(
            self.search_frame,
            width=3,
            text=msg.SS_SPEC,
            command=self.toggleMaxSpec
        )
        self.search_sp.config(relief=tk.SUNKEN)
        ToolTip(self.search_sp, msg.SS_TT_SHOW_SPEC)
        self.search_sp.pack(side=tk.LEFT)
        self.search_box = tk.Entry(
            self.search_frame,
            textvariable=self.search
        )
        ToolTip(self.search_box, msg.SS_TT_SEARCH)
        self.search_box.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.search_button = tk.Button(
            self.search_frame,
            text=msg.SS_SEARCH,
            command=lambda:
                self._showSkills(search=True)
        )
        self.search_button.pack(side=tk.RIGHT)
        self.search_frame.pack(fill=tk.X, expand=1)
        self.frame = tk.Frame(self)
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.list_box = tk.Treeview(self.frame)
        self.list_box.bind("<<TreeviewSelect>>", self._selectionChanged)
        self.list_box.config(
            selectmode=tk.EXTENDED,
            yscrollcommand=self.scrollbar.set,
            height=20,
            show="tree",
        )
        self.scrollbar.config(command=self.list_box.yview)
        self.list_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.frame.pack(fill=tk.BOTH)
        
        self.new_skill_name = tk.StringVar()
        self.new_skill_name.set(msg.SS_NEW_SKILL)
        self.new_skill_name.trace(
            "w",
            lambda name, empty, mode:
                self._newSkillName()
        )
        self.new_skill_check = False
        self.new_skill_entry = tk.Entry(
            self,
            textvariable=self.new_skill_name,
            state=tk.DISABLED
        )
        self.new_skill_entry.bind("<FocusIn>", self._skillEntryFocus)
        self.new_skill_entry.bind("<FocusOut>", self._skillEntryNoFocus)

        self.new_skill_entry_focus = False
        self.new_skill_entry.pack(fill=tk.X)

        self.add_button_text = tk.StringVar()
        self.add_button = tk.Button(
            self,
            textvariable=self.add_button_text,
            command=self.addSkills,
            state=tk.DISABLED
        )
        if self.char.getEditMode() == "generation":
            self.add_button_text.set(msg.SS_ADD_REMOVE_SKILLS)
        else:
            self.add_button_text.set(msg.SS_ADD_SKILLS)
        self.add_button.pack(fill=tk.X)
        
        self._showSkills()
        self.focus()

    def _showSkills(self, minspec=1, maxspec=3, search=False):
        """ Displaying the skills in the list box

        Args:
            minspec(int): minimum specialization level to display (1-3)
            maxspec(int): maximum specialization level to display (1-3)
            search(bool)=False - if true the search box will be evaluated
        """

        children = self.list_box.get_children()
        self.list_box.delete(*children)
        skills = self.all_skills.getList(minspec, maxspec)
        
        # skills the character already owns
        cur_skills = [skill.get("name") for skill in self.char.getSkills()]

        # filter for search mode ... 
        if search: 
            search_term = self.search.get()
            skills = [skill for skill in skills
                      if search_term.lower() in skill[0].lower()]

        sk_dict = {}

        for skill in skills:
            name, spec, id, parent = skill
            if name in cur_skills:
                image = self.sel_icon
            else:
                image = self.unsel_icon

            # making sure that ids are unique
            while sk_dict.get(id):
                id *= 10

            if sk_dict.get(parent):
                sk_dict[id] = self.list_box.insert(
                    sk_dict[parent],
                    100,
                    iid=id,
                    text=name,
                    image=image
                )
            else:
                sk_dict[id] = self.list_box.insert(
                    "",
                    100,
                    text=name,
                    image=image
                )

    def toggleMinSpec(self):
        """ Toggles minimum specialization between 1 and 2

        Note:
            called as command on a button.
        """

        if self.minspec == 1:
            self.minspec = 2
            self.search_gf.config(relief=tk.RAISED)
        else:
            self.minspec = 1
            self.search_gf.config(relief=tk.SUNKEN)
        self._showSkills(self.minspec, self.maxspec)

    def toggleMaxSpec(self):
        """ Toggles maximum specialization between 2 and 3

        Note:
            called as command on a button.
        """

        if self.maxspec == 3:
            self.maxspec = 2
            self.search_sp.config(relief=tk.RAISED)
        else:
            self.maxspec = 3
            self.search_sp.config(relief=tk.SUNKEN)
        self._showSkills(self.minspec, self.maxspec)

    #  player presses the add skills button
    def addSkills(self):
        """ Adding/Removing the selected skills

        Note:
            called as command on the button
        presses the button 
        """

        selection = self.list_box.selection()

        # adding a new skill ...
        new_skill_name = self.new_skill_name.get()
        if new_skill_name != msg.SS_NEW_SKILL and self.origin != "":
            origin = self.origin
            skill = new_skill_name
            self.all_skills.newSkill(skill, origin)
            skill_element = self.all_skills.getSkill(skill)
            self.char.addSkill(skill_element)

        # ... or adding / removing existing skills ...
        else:
            for id in selection:
                skill = self.list_box.item(id)
                icon = skill.get("image")[0]
                skill_name = skill.get("text")
                if icon == str(self.unsel_icon):
                    skill_element = self.all_skills.getSkill(skill_name)
                    self.char.addSkill(skill_element)
                else:
                    self.char.delSkill(skill_name)

        # finally close the window
        self.app.updateSkillList()
        self.close()
    
    # handle selection changes
    def _selectionChanged(self, event):
        """ Updating relevant UI elements on selection changes """

        selection = self.list_box.selection()
        
        # list of items to add / remove ...
        add = []
        remove = []
        for id in selection:
            item = self.list_box.item(id)
            icon = item.get("image")[0]
            if icon == str(self.unsel_icon):
                add.append(item)
            else:
                remove.append(item)

        if len(selection) == 0 and not self.new_skill_entry_focus:
            self.new_skill_entry.config(state=tk.DISABLED)
            self.new_skill_name.set(msg.SS_NEW_SKILL)
            self.add_button.config(state=tk.NORMAL)
            self.origin = ""

        if len(selection) == 1:
            self.new_skill_entry.config(state=tk.NORMAL)
            self.add_button.config(state=tk.NORMAL)
            if add:
                self.add_button_text.set(msg.SS_ADD_SINGLE_SKILL)
            else:
                self.add_button_text.set(msg.SS_REMOVE_SINGLE_SKILL)

            origin = self.list_box.item(selection[0])
            origin = origin.get("text")
            self.origin = origin

        if len(selection) > 1:
            self.new_skill_entry.config(state=tk.DISABLED)
            self.new_skill_name.set(msg.SS_NEW_SKILL)
            self.add_button.config(state=tk.NORMAL)
            self.origin = ""
            if add and not remove:
                text = msg.SS_ADD_MULTIPLE_SKILLS.format(add=len(add))
                self.add_button_text.set(text)
            if add and remove:
                text = msg.SS_ADD_REMOVE_MULTIPLE_SKILLS.format(
                    add=len(add),
                    rem=len(remove)
                )
                self.add_button_text.set(text)
            if remove and not add:
                text = msg.SS_REMOVE_MULTIPLE_SKILLS.format(rem=len(remove))
                self.add_button_text.set(text)

    # clear entry field on focus
    def _skillEntryFocus(self, event):
        """ This method clears the name entry field for a new skill once it gets
        focus. As selecting on it would clear the selection of the listbox
        """

        self.new_skill_entry_focus = True
        new_name = self.new_skill_name.get()
        if new_name == msg.SS_NEW_SKILL:
            self.new_skill_name.set("")

    def _skillEntryNoFocus(self, event):
        self.new_skill_entry_focus = False
        self.list_box.config(state=tk.NORMAL)

    # checks the name of a potential skill 
    def _newSkillName(self):
        """ this method checks the entered name for a new skill. 
        In case it contains illegal chars or is a duplicate of an existing name
        the 'add skill' button will be disabled and the text marked red. 
        it is called as trace on the tk.Stringvar() 

        """
        new_name = self.new_skill_name.get()
        name_exists = False
        illegal_chars = False
        if new_name in self.complete_list:
            name_exists = True
        regex_string = "[^a-zA-Z0-9 .,:\(\)\[\]\!\xE4\xF6\xFC\xC4\xD6\xDC\xDF]" 
        if re.findall(regex_string, new_name):
            illegal_chars = True
        
        if name_exists or illegal_chars: 
            self.new_skill_entry.config(foreground="#ff0000")
            self.add_button.config(state=tk.DISABLED)
            if name_exists:
                self.add_button_text.set(msg.SS_SKILL_EXISTS)
            if illegal_chars:
                self.add_button_text.set(msg.SS_ILLEGAL_CHARS)
        else: 
            self.new_skill_entry.config(foreground="#000000")
            self.add_button.config(state=tk.NORMAL)
            self.add_button_text.set(msg.SS_NEW_SKILL)

    def close(self):
        self.destroy()
        self.app.open_windows["skill"] = 0
