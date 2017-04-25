import tk_ as tk
from PIL import ImageTk
import config
from socialeditor import SocialEditor

msg = config.Messages()

class SocialScreen(tk.Frame):
    """ The social screen displays the characters contacts in the main window

    main (tk.Tk): holding the program
    app (Application): the programs primary screen 
    """

    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.char = app.char
        self.open_windows = app.open_windows

        # resizing stuff
        self.elements = 3
        self.height = 160

        self.contact_canvas = tk.Canvas(self, width=1, height=1)
        self.contact_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.contact_scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.contact_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.contact_scroll.config(command=self.contact_canvas.yview)
        self.contact_canvas.config(yscrollcommand=self.contact_scroll.set)
        self.contact_canvas.bind("<Configure>", self.resize)
        self.showContacts(self.contact_canvas)

    def resize(self, event):
        w = event.width
        old_elements = self.elements
        self.elements = w // 250

        if self.elements != old_elements:
            self.showContacts(self.contact_canvas)

    # show all contacts
    def showContacts(self, canvas):
        """ display all contacts 
        
        canvas (tk.Canvas): the canvas to draw on 
        """

        # clear canvas
        canvas.delete("all")

        # prepare layouting variables
        row = 0
        col = 0
        width = canvas.winfo_width()
        # retrieve contacts
        contacts = self.char.getContacts()

        for contact in contacts:
            # automatically remove contacts that were created
            # but never stored ... 
            if contact.get("xp") is None:
                id = contact.get("id")
                self.char.removeContactById(id)

            # render contact to canvas ... 
            else:

                id = contact.get("id")

                contact_frame = ContactFrame(
                    canvas,
                    contact=contact
                )
                contact_frame.bind(
                    "<Button-1>",
                    lambda event, id=id: self.editContact(id)
                )

                # draw box to canvas
                x = col * width / self.elements,
                y = row * self.height,

                canvas.create_window(
                    x,
                    y,
                    width=width / self.elements,
                    height=self.height,
                    anchor=tk.NW,
                    window=contact_frame
                )

                # set grid location for next box ...
                col += 1
                if col >= self.elements:
                    col = 0
                    row += 1

        # finally add a button to add contacts ... 
        plus_image = ImageTk.PhotoImage(file="img/plus.png")
        new_button = tk.Button(
            canvas,
            image=plus_image,
            command=self.newContact
        )
        new_button.image = plus_image
        # draw box to canvas
        x = col * width / self.elements,
        y = row * self.height,

        canvas.create_window(
            x,
            y,
            width=width / self.elements,
            height=self.height,
            anchor=tk.NW,
            window=new_button
        )

        self.contact_canvas.config(
            scrollregion=(0, 0, 1, (row+1)*self.height)
        )

    def newContact(self):
        """ adds a new contact and opens the contact editor """

        new_id = self.char.newContact("")
        contact = self.char.getContactById(new_id)
        self.displaySocialEditor(contact)

    def editContact(self, id):
        """ opens the contact editor to edit a contact"""

        contact = self.char.getContactById(id)
        self.displaySocialEditor(contact)

    def displaySocialEditor(self, contact):
        """ this actually calls the contact editor """

        if self.app.open_windows["contact"] == 0:
            SocialEditor(self, contact)
        else: 
            self.app.open_windows["contact"].close()
            SocialEditor(self, contact)


class ContactFrame(tk.Frame):
    """ Widget for displaying a character in the social screen
    
    Note:
        Subclasses tk.Frame, so you can do everything you can do 
        with a frame. 
    
    Args: 
        master: the parent widget/tk instance
        contact (et.Element<contact>): the contact to display
    """

    def __init__(self, master=None, contact=None, **kwargs):
        super().__init__(master, **kwargs)

        contact_frame = tk.LabelFrame(self, text=msg.SE_CONTACT_TITLE)
        contact_frame.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1,
            anchor=tk.NW
        )
        name = contact.get("name", "")
        name_label = tk.Label(
            self,
            text=name,
            font=config.Style.ATTR_FONT,
            anchor=tk.E
        )
        name_label.place(
            relx=.5,
            rely=.3,
            anchor=tk.CENTER
        )

        competency = "{name} ({lvl})".format(
            name=contact.get("competency", ""),
            lvl=contact.get("competencylevel", "")
        )
        comp_label=tk.Label(contact_frame, text=competency)
        comp_label.place(
            relx=.5,
            rely=.6,
            anchor=tk.CENTER
        )

        location = contact.get("location", "")
        loc_label = tk.Label(contact_frame, text=location)
        loc_label.place(
            relx=.5,
            rely=.8,
            anchor=tk.CENTER
        )

        # the contacts loyality is used to recolor the name ...
        loyality = float(contact.get("loyality", "0"))
        if loyality >= 1:
            name_label.config(foreground=config.Colors.DARK_GREEN)
        if loyality < 0:
            name_label.config(foreground=config.Colors.DARK_RED)
        if 0 <= loyality < 1:
            name_label.config(foreground=config.Colors.BLACK)

    def bind(self, sequence=None, func=None, add=None):
        """ overrides bind to bind to all parts of the widget """

        widgets = self.winfo_children()
        for widget in widgets:
            widget.bind(sequence, func, add)
        return super().bind(sequence, func, add)


