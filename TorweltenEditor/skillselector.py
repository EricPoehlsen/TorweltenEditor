# coding=utf-8
""" This module is responsible for the skill selection window """

import config
import tkinter as tk
import re

msg = config.Messages()

# this class creates a SkillSelectionWindow        
class SkillSelector:
    def __init__(self,main):
        
        #  point to character and skilltree
        self.char = main.char
        self.all_skills = main.skills
        self.main = main
        self.minspec = 1
        self.maxspec = 3
        self.origin = ""
        self.complete_list = [skill[0] for skill in self.all_skills.list()]

        #  build the window
        self.skill_editor = tk.Toplevel()
        if self.char.getEditMode == "generation":
            self.skill_editor.title(msg.SS_ADD_REMOVE_SKILLS)
        else:
            self.skill_editor.title(msg.SS_ADD_SKILLS)
        self.skill_editor.protocol("WM_DELETE_WINDOW", self.close)
        self.search_frame = tk.Frame(self.skill_editor)
        self.search = tk.StringVar()
        self.search_gf = tk.Button(self.search_frame,
                                   text = msg.SS_BASE, 
                                   relief = tk.SUNKEN, 
                                   command = self.toggleMinSpec)
        self.search_gf.pack(side=tk.LEFT)
        self.search_sp = tk.Button(self.search_frame,
                                   text = msg.SS_SPEC,
                                   relief = tk.SUNKEN,
                                   command = self.toggleMaxSpec)
        self.search_sp.pack(side=tk.LEFT)
        self.search_box = tk.Entry(self.search_frame,
                                   textvariable = self.search)
        self.search_box.pack(side=tk.LEFT,fill = tk.X, expand = 1)
        self.search_button = tk.Button(self.search_frame, 
                                       text = msg.SS_SEARCH, 
                                       command = self._searchSkills)
        self.search_button.pack(side = tk.RIGHT)
        self.search_frame.pack(fill = tk.X, expand = 1)
        self.frame = tk.Frame(self.skill_editor)
        self.scrollbar = tk.Scrollbar(self.frame,orient = tk.VERTICAL)
        self.list_box = tk.Listbox(self.frame)
        self.list_box.bind("<<ListboxSelect>>",self._selectionChanged)
        self.list_box.config(selectmode = tk.MULTIPLE, 
                             yscrollcommand = self.scrollbar.set, 
                             height = 20, 
                             selectbackground = "#0000dd")
        self.scrollbar.config(command = self.list_box.yview)
        self.list_box.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        self.scrollbar.pack(side = tk.RIGHT, fill=tk.Y)
        self.frame.pack(fill = tk.BOTH)
        
        self.new_skill_name = tk.StringVar()
        self.new_skill_name.set(msg.SS_NEW_SKILL)
        self.new_skill_name.trace("w",lambda name,empty,mode: self._newSkillName())
        self.new_skill_check = False
        self.new_skill_entry = tk.Entry(self.skill_editor,
                                        textvariable = self.new_skill_name, 
                                        state = tk.DISABLED)
        self.new_skill_entry.bind("<FocusIn>",self._skillEntryFocus)
        self.new_skill_entry.pack(fill = tk.X)

        self.add_button_text = tk.StringVar()
        if self.char.getEditMode() == "generation": 
            self.add_button_text.set(msg.SS_ADD_REMOVE_SKILLS)
        else: 
            self.add_button_text.set(msg.SS_ADD_SKILLS)
        self.add_button = tk.Button(self.skill_editor, 
                                    textvariable = self.add_button_text, 
                                    command = self.addSkills, 
                                    state = tk.DISABLED)
        self.add_button.pack(fill = tk.X)
        
        self._showSkills()
        self.skill_editor.focus()


    
    # event handler for search button ...
    def _searchSkills(self):
        """ run _showSkills with search=True """
        self._showSkills(self.minspec, self.maxspec, search=True)

    # display the skills in the list_box
    def _showSkills(self, minspec=1, maxspec=3, search=False):
        """ this method will display skills in the listbox 
        minspec: int - minimum specialization level to display (1-3)
        maxspec: int - maximum specialization level to display (1-3)
        search: bool - true if the search_box shall be avaluated
        """
        # clear the list
        self.list_box.delete(0,tk.END)
        
        # the base list already takes care for the specification limit
        skills = self.all_skills.list(minspec,maxspec)
        
        # skills the character already owns
        cur_skills = self.char.getSkillList()

        # filter for search mode ... 
        if search: 
            search_term = self.search.get()
            skills = [skill for skill in skills if search_term.lower() in skill[0].lower()]

        # filter skills the charakter already has ...             
        if self.char.getEditMode() == "generation":
            def append_delete(skill):
                skill = [skill[0],skill[1],skill[2]]
                if skill[0] in cur_skills:
                    skill[0] += msg.SS_X
                return skill
            skills = [append_delete(skill) for skill in skills]
        else:    
            skills = [skill for skill in skills if skill[0] not in cur_skills]
                    
        # indent based on specialization.             
        skills = [[(skill[1]-minspec)*4*" " + skill[0],skill[1],skill[2]] for skill in skills] 

        # now add the skills ... 
        for skill in skills:
            self.list_box.insert(tk.END,skill[0])

    # toggle min spec level    
    def toggleMinSpec(self):
        """ called as button click, this method switches the minimum
        specialization limit to show or hide 'base skills'
        """

        if self.minspec == 1:
            self.minspec = 2
            self.search_gf.config(relief = tk.RAISED)
        else:
            self.minspec = 1
            self.search_gf.config(relief = tk.SUNKEN)
        self.showSkills(self.minspec,self.maxspec)

    # toggle max spec level
    def toggleMaxSpec(self):
        """ called as button click, this method switches the maximum
        specialization limit to show or hide 'specializations'
        """

        if self.maxspec == 3:
            self.maxspec = 2
            self.search_sp.config(relief = tk.RAISED)
        else:
            self.maxspec = 3
            self.search_sp.config(relief = tk.SUNKEN)
        self.showSkills(self.minspec,self.maxspec)

    #  player presses the add skills button
    def addSkills(self):
        """ This method adds / removes skills once the player
        presses the button 
        """

        selection = self.list_box.curselection()

        # adding a new skill ...
        new_skill_name = self.new_skill_name.get()
        if new_skill_name != msg.SS_NEW_SKILL and self.origin != "":
            origin = self.origin.replace(msg.SS_X,"")
            skill = new_skill_name
            self.all_skills.newSkill(skill,origin)
            self.char.addSkill(skill)

        # ... or adding / removing existing skills ...
        else:
            for item in selection:
                skill_name = self.list_box.get(item).strip()
                if (msg.SS_X in skill_name):
                    self.char.delSkill(skill_name[:-len(msg.SS_X)])
                else:
                    self.char.addSkill(skill_name)
        
        # finally close the window
        self.main.updateSkillList()
        self.close()
    
    # handle selection changes
    def _selectionChanged(self,event):
        """ This method handles changes in the selection in the listbox and 
        applies appropriate changes to the relevant UI elements based on the 
        number of selected entries. 
        """

        self.list_box.config(selectbackground = "#0000dd")
        selection = self.list_box.curselection()
        
        # list of items to add / remove ...
        add =  [item for item in selection if msg.SS_X not in self.list_box.get(item)]
        remove = [item for item in selection if msg.SS_X in self.list_box.get(item)]
           
        if len(selection) == 0:
            self.new_skill_entry.config(state = tk.DISABLED)
            self.new_skill_name.set(msg.SS_NEW_SKILL)
            self.add_button.config(state = tk.NORMAL)
            self.origin = ""

        if len(selection) == 1:
            self.new_skill_entry.config(state = tk.NORMAL)
            self.add_button.config(state = tk.NORMAL)
            if add: self.add_button_text.set(msg.SS_ADD_SINGLE_SKILL)
            else: self.add_button_text.set(msg.SS_REMOVE_SINGLE_SKILL)
            self.origin = self.list_box.get(selection[0]).strip().replace(msg.SS_X,"")

        if len(selection) > 1:
            self.new_skill_entry.config(state = tk.DISABLED)
            self.new_skill_name.set(msg.SS_NEW_SKILL)
            self.add_button.config(state = tk.NORMAL)
            self.origin = ""
            if add and not remove:
                self.add_button_text.set(msg.SS_ADD_MULTIPLE_SKILLS %(len(add)))
            if add and remove:
                self.add_button_text.set(msg.SS_ADD_REMOVE_MULTIPLE_SKILLS %(len(add),len(remove)))
            if remove and not add:
                self.add_button_text.set(msg.SS_REMOVE_MULTIPLE_SKILLS %(len(remove)))

    # clear entry field on focus
    def _skillEntryFocus(self,event):
        """ This method clears the name entry field for a new skill once it gets
        focus. As selecting on it would clear the selection of the listbox
        """
        new_name = self.new_skill_name.get()
        if new_name == msg.SS_NEW_SKILL:
            self.new_skill_name.set("")
        self.list_box.config(selectbackground = "#00bb00")

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
        if new_name in self.complete_list: name_exists = True
        regex_string = "[^a-zA-Z0-9 .,:\(\)\[\]\!\xE4\xF6\xFC\xC4\xD6\xDC\xDF]" 
        if re.findall(regex_string,new_name): illegal_chars = True
        
        if name_exists or illegal_chars: 
            self.new_skill_entry.config(foreground = "#ff0000")
            self.add_button.config(state = tk.DISABLED)
            if name_exists: self.add_button_text.set(msg.SS_SKILL_EXISTS)
            if illegal_chars: self.add_button_text.set(msg.SS_ILLEGAL_CHARS)
        else: 
            self.new_skill_entry.config(foreground = "#000000")
            self.add_button.config(state = tk.NORMAL)
            self.add_button_text.set(msg.SS_NEW_SKILL)

    def close(self):
        self.skill_editor.destroy()
        self.main.open_windows["skill"] = 0

