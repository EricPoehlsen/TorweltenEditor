import xml.etree.ElementTree as et
import tkinter as tk
import config

msg = config.Messages()


class SocialEditor(tk.Toplevel):
    """ displaying a window to edit a characters contact

    app (Application): the main instance of the program
    contact (et.Element<contact>: the contact to edit
    """

    def __init__(self, app, contact):
        tk.Toplevel.__init__(self, app)
        self.app = app
        self.app.open_windows["contact"] = self

        self.char = app.char
        self.contact = contact
        self.vars = {}
        self.xp_cost = tk.IntVar()
        self.changes = []
        self.delete_check = False

        self.main_screen = tk.Frame(self)
        self.bottom_menu = tk.Frame(self)
        self.showContact(self.main_screen)
        self.showMenu(self.bottom_menu)
        self.updateMenu(self.bottom_menu)

        self.main_screen.pack(fill=tk.BOTH, anchor=tk.NW)
        self.bottom_menu.pack(side=tk.BOTTOM, anchor=tk.S, fill=tk.X)

        self.protocol("WM_DELETE_WINDOW", self.close)

    def showMenu(self,frame):
        widgets = frame.winfo_children()
        for widget in widgets: widget.destroy()

        close = tk.Button(
            frame,
            text=msg.SE_CLOSE,
            command=self.close
            )
        close.pack(side=tk.LEFT)

        save = tk.Button(
            frame,
            text=msg.SE_SAVE,
            command=self.updateContact
            )
        save.pack(side=tk.LEFT)

        delete = tk.Button(
            frame,text=msg.SE_DELETE,
            command=self.deleteContact
            )
        delete.pack(side=tk.LEFT)

        xp = tk.Label(frame, text=msg.XP+": ")
        xp.pack(side=tk.LEFT, anchor=tk.E)
        xp_val = tk.Label(frame, textvariable=self.xp_cost)
        xp_val.pack(side=tk.LEFT, anchor=tk.E)

    # updating menu items if necessary ...
    def updateMenu(self, frame):
        """ This methos is used to update the menu items
        """
        widgets = frame.winfo_children()
        for widget in widgets:
            if widget.cget("text") == msg.SE_SAVE:
                if self.wasChanged():
                    widget.config(state=tk.NORMAL)
                else:
                    widget.config(state=tk.DISABLED)
            if widget.cget("text") == msg.SE_DELETE:
                if self.delete_check is True:
                    widget.config(background="#ff0000")
                else: 
                    widget.config(background="#dddddd")

    # display the contact information ...
    def showContact(self, frame):
        """
        This method creates the information screen, adds respective variables and links the traces ...
        frame: the tkinter content frame in which the data shall be shown
        """

        # clear any old widgets ...
        widgets = self.main_screen.winfo_children()
        for widget in widgets:
            widget.destroy()

        # setup the screen and the variables
        self.vars["name"] = tk.StringVar()
        name_frame = tk.LabelFrame(
            frame,
            text=msg.NAME
            )
        name_entry = tk.Entry(
            name_frame,
            textvariable=self.vars["name"]
            )
        name_entry.pack(fill=tk.X)
        name_frame.pack(fill=tk.X)

        self.vars["location"] = tk.StringVar()
        location_frame = tk.LabelFrame(
            frame,
            text=msg.SE_LOCATION
            )
        location_entry = tk.Entry(
            location_frame,
            textvariable=self.vars["location"]
            )
        location_entry.pack(fill=tk.X)
        location_frame.pack(fill=tk.X)

        self.vars["competency"] = tk.StringVar()
        self.vars["competency_level"] = tk.StringVar()
        competency_frame = tk.LabelFrame(
            frame,
            text=msg.SE_COMPETENCY
            )
        competency_entry = tk.Entry(
            competency_frame,
            textvariable=self.vars["competency"]
            )
        competency_level = tk.Spinbox(
            competency_frame,
            from_=1,
            to=9,
            textvariable=self.vars["competency_level"],
            width=2
            )
        competency_entry.pack(side=tk.LEFT, fill=tk.X, expand=1)
        competency_level.pack(side=tk.LEFT, anchor=tk.E)
        competency_frame.pack(fill=tk.X)

        self.vars["loyality"] = tk.StringVar()
        self.vars["loyality_level"] = tk.StringVar()
        loyality_frame = tk.LabelFrame(
            frame,
            text = msg.SE_LOYALITY
            )
        loyality_label = tk.Label(
            loyality_frame,
            textvariable=self.vars["loyality"]
            )
        loyality_label.pack(fill=tk.X)
        loyality_level = tk.Scale(
            loyality_frame,
            from_=-3,
            to=3,
            variable=self.vars["loyality_level"],
            showvalue=0,
            orient=tk.HORIZONTAL
            )
        loyality_level.pack(fill=tk.X)
        loyality_frame.pack(fill=tk.X)

        self.vars["frequency"] = tk.StringVar()
        self.vars["frequency_level"] = tk.StringVar()
        frequency_frame = tk.LabelFrame(
            frame,
            text=msg.SE_FREQUENCY
            )
        frequency_label = tk.Label(
            frequency_frame,
            textvariable=self.vars["frequency"]
            )
        frequency_label.pack(fill= tk.X)
        frequency_level = tk.Scale(
            frequency_frame,
            from_=0,
            to=5,
            variable=self.vars["frequency_level"],
            showvalue=0,
            orient=tk.HORIZONTAL)
        frequency_level.pack(fill=tk.X)
        frequency_frame.pack(fill=tk.X)

        description_frame = tk.LabelFrame(
            frame,
            text=msg.SE_DESCRIPTION
            )
        description_text = tk.Text(
            description_frame,
            width=40,
            height=10,
            wrap=tk.WORD,
            font="Arial 9"
            )
        description_text.bind(
            "<KeyRelease>",
            self.descriptionChanged
            )
        description_text.pack(fill=tk.X)
        description_frame.pack(fill=tk.X)

        # adding the traces ...
        # needs to be down here to make sure all variables exist
        variables = [
            "name",
            "location",
            "competency",
            "competency_level",
            "loyality_level",
            "frequency_level"
            ]

        for variable in variables:
            self.vars[variable].trace("w", self.dataChanged)

        # TODO: maybe clean this up ...
        self.vars["name"].set(self.contact.get("name"))
        self.vars["location"].set(self.contact.get("location", ""))
        self.vars["loyality_level"].set(self.contact.get("loyality", "0"))
        stored_frequency = float(self.contact.get("frequency", "1.0"))
        frequencies = { 0.25: 0, 0.5: 1, 0.75: 2, 1.0: 3, 1.5: 4, 2.0: 5}
        self.vars["frequency_level"].set(frequencies[stored_frequency])
        self.vars["competency_level"].set(self.contact.get("competencylevel", "4"))
        self.vars["competency"].set(self.contact.get("competency", ""))
        
        self.vars["description"] = None
        description = self.contact.find("description")
        if description is not None:
            self.vars["description"] = description.text
        if self.vars["description"] is None:
            self.vars["description"] = ""
        description_text.insert(tk.END,self.vars["description"])
    
    # trace callback for most of the data ...
    def dataChanged(self, name, e, m):
        """ Trace method used for tk.IntVar() and tk.StringVar() 
        basically tracking everything but the description text field

        name(string): the tk name of the variable
        e, m(string): unused from .trace()
        """        
        
        # get the traces
        frequency_name = str(self.vars["frequency_level"])
        competency_name = str(self.vars["competency_level"])
        competency_type = str(self.vars["competency"])
        loyality_name = str(self.vars["loyality_level"])
        location_name = str(self.vars["location"])
        name_name = str(self.vars["name"])

        # loyality changed
        if name == loyality_name:
            loyality_var = float(self.vars["loyality_level"].get())
            
            if loyality_var == -3: self.vars["loyality"].set(msg.SE_ENEMY_3)
            elif loyality_var == -2: self.vars["loyality"].set(msg.SE_ENEMY_2)
            elif loyality_var == -1: self.vars["loyality"].set(msg.SE_ENEMY_1)
            elif loyality_var == 0: self.vars["loyality"].set(msg.SE_CONTACT)
            elif loyality_var == 1: self.vars["loyality"].set(msg.SE_FRIEND_1)
            elif loyality_var == 2: self.vars["loyality"].set(msg.SE_FRIEND_2)
            elif loyality_var == 3: self.vars["loyality"].set(msg.SE_FRIEND_3)

            self.calculateCosts()

        # frequency changed            
        elif name == frequency_name:
            freq_var = int(self.vars["frequency_level"].get())
            if freq_var == 0: self.vars["frequency"].set(msg.SE_FREQUENCY_0)
            elif freq_var == 1: self.vars["frequency"].set(msg.SE_FREQUENCY_1)
            elif freq_var == 2: self.vars["frequency"].set(msg.SE_FREQUENCY_2)
            elif freq_var == 3: self.vars["frequency"].set(msg.SE_FREQUENCY_3)
            elif freq_var == 4: self.vars["frequency"].set(msg.SE_FREQUENCY_4)
            elif freq_var == 5: self.vars["frequency"].set(msg.SE_FREQUENCY_5)

            self.calculateCosts()

        # competency level changed            
        elif name == competency_name:
            competency = self.vars["competency_level"].get()
            try: 
                competancy = int(competency)
            except ValueError:
                competency = 1
                self.vars["competency_level"].set("1")

            self.calculateCosts()

        # these are just for completeness ...
        # competency type changed
        elif name == competency_type:
            pass

        # name changed
        elif name == name_name:
            pass

        # location changed 
        elif name == location_name:
            pass

        # reset delete check, update menu ... 
        self.delete_check = False
        self.updateMenu(self.bottom_menu)

    # bind callback for the description text widget ...
    def descriptionChanged(self, event):
        """ tracking changes in the description text field
        stores the current content into the variables for later use ...

        event(tk.Event): incoming event
        """
        widget = event.widget
        self.vars["description"] = widget.get("1.0", tk.END)
        self.delete_check = False
        self.updateMenu(self.bottom_menu)

        if "description" not in self.changes:
            self.changes.append("description")
            print("added")

    # check if something was changed
    def wasChanged(self):
        """ This method is called to find out if the contact was changed

        so if the user just moves around the sliders but finally they are
        in the original position there was no change.

        return: True if changes are detected
        """

        changed = False

        new_name = self.vars["name"].get()
        old_name = self.contact.get("name", "")
        if new_name != old_name:
            changed = True
            self.changes.append("name")

        new_location = self.vars["location"].get()
        old_location = self.contact.get("location", "")
        if new_location != old_location:
            changed = True
            self.changes.append("location")

        new_competency = self.vars["competency"].get()
        old_competency = self.contact.get("competency", "")
        if new_competency != old_competency:
            changed = True
            self.changes.append("competency")

        new_competency_level = self.vars["competency_level"].get()
        old_competency_level = self.contact.get("competencylevel", "")
        if new_competency_level != old_competency_level:
            changed = True
            self.changes.append("competency")

        frequency_var = int(self.vars["frequency_level"].get())
        frequencies = {0: 0.25, 1: 0.5, 2: 0.75, 3: 1.0, 4: 1.5, 5: 2.0}
        new_frequency_level = str(frequencies[frequency_var])
        old_frequency_level = self.contact.get("frequency", "")
        if new_frequency_level != old_frequency_level:
            changed = True
            self.changes.append("frequency")

        new_loyality_level = self.vars["loyality_level"].get()
        old_loyality_level = self.contact.get("loyality", "")
        if new_loyality_level != old_loyality_level:
            changed = True
            self.changes.append("loyality")

        new_description = self.vars["description"]
        old_description = self.contact.text
        if old_description is None: old_description = ""
        if new_description != old_description:
            changed = True

        return changed
    
    # actually updating the contact ...
    def updateContact(self):
        old_name = self.contact.get("name")
        frequency_var = int(self.vars["frequency_level"].get())
        frequencies = {0: 0.25, 1: 0.5, 2: 0.75, 3: 1.0, 4: 1.5, 5: 2.0}
        new_frequency = str(frequencies[frequency_var])

        new_competency = str(self.vars["competency"].get())
        new_competency_level = str(self.vars["competency_level"].get())
        new_loyality = int(float(self.vars["loyality_level"].get()))
        if new_loyality == 0:
            new_loyality = 0.5
        new_loyality = str(new_loyality)

        new_name = str(self.vars["name"].get())
        new_location = str(self.vars["location"].get())

        old_xp = int(self.contact.get("xp", "0"))
        new_xp = int(self.xp_cost.get()) + old_xp
        xp_string = str(new_xp)

        # set the new data ...
        self.contact.set("name", new_name)
        self.contact.set("location", new_location)
        self.contact.set("loyality", new_loyality)
        self.contact.set("frequency", new_frequency)
        self.contact.set("competencylevel", new_competency_level)
        self.contact.set("competency", new_competency)
        self.contact.set("xp", xp_string)

        description = self.contact.find("description")
        if description is None: 
            description = et.SubElement(self.contact, "description")
        description.text = self.vars["description"]

        self.app.showContacts(self.app.contact_canvas)

        self.char.updateAvailableXP(-int(self.xp_cost.get()))
        self.calculateCosts()
        self.updateMenu(self.bottom_menu)
        self.changes = set(self.changes)
        op = None
        if "name" in self.changes:
            op = old_name
        self.char.logEvent(self.contact, mod=self.changes, op=op)
        self.changes = []

    def calculateCosts(self):
        old_xp = int(self.contact.get("xp", "0"))

        new_frequency = 0
        frequency_var = int(self.vars["frequency_level"].get())
        frequencies = {0: 0.25, 1: 0.5, 2: 0.75, 3: 1.0, 4: 1.5, 5: 2.0}
        new_frequency = frequencies[frequency_var]

        new_competency = int(self.vars["competency_level"].get())
        new_loyality = float(self.vars["loyality_level"].get())
        if new_loyality == 0:
            new_loyality = 0.5

        xp_cost = new_competency * new_loyality * new_frequency

        xp_cost_round = round(xp_cost, 0)
        if xp_cost_round == 0 and xp_cost > 0:
            xp_cost_round = 1
        if xp_cost_round == 0 and xp_cost < 0:
            xp_cost_round = -1

        self.xp_cost.set(int(xp_cost_round - old_xp))

    def deleteContact(self):
        if self.delete_check:
            contact_id = self.contact.get("id")
            
            # if generation mode, return spent/gained xp
            edit_mode = self.char.getEditMode()
            if edit_mode == "generation":
                xp = int(self.contact.get("xp", "0"))
                self.char.updateAvailableXP(xp)

            # remove contact, update list and close window ...
            self.char.removeContactById(contact_id)
            self.app.showContacts(self.app.contact_canvas)
            self.close()
        else:
            self.delete_check = True
            self.updateMenu(self.bottom_menu)

    def close(self):
        self.app.open_windows["contact"] = 0
        self.destroy()
