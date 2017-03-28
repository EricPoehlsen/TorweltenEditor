# coding=utf-8
import tkinter as tk
import config
from socialeditor import SocialEditor


class SocialScreen(tk.Frame):
    """ The social screen displays the characters contacts in the main window

    main (tk.Tk): holding the program
    app (Application): the programs primary screen 
    """

    def __init__(self, main, app):
        tk.Frame.__init__(self,main)
        self.app = app
        self.char = app.char
        self.open_windows = app.open_windows
        # create canvas ... 
        self.contact_canvas = tk.Canvas(self, width=770, height=540)
        self.contact_canvas.pack(side = tk.LEFT)
        self.contact_scroll = tk.Scrollbar(self,orient = tk.VERTICAL)
        self.contact_scroll.pack(side = tk.LEFT, fill = tk.Y) 
        self.contact_scroll.config(command = self.contact_canvas.yview)
        self.contact_canvas.config(yscrollcommand = self.contact_scroll.set)

        self.showContacts(self.contact_canvas)

    # show all contacts
    def showContacts(self, canvas):
        """ display all contacts 
        
        canvas (tk.Canvas): the canvas to draw on 
        """

        # clear canvas
        canvas.delete(tk.ALL)

        # prepare layouting variables
        row = 0
        col = 0
        width = canvas.winfo_reqwidth()/3 - 5
        height = 80

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
                
                box = tk.Label(canvas, borderwidth = 2, relief = tk.RIDGE)
                id = contact.get("id")

                # the contacts name ...
                name = contact.get("name","")
                name_label = tk.Label(box, text = name, font = "Arial 12 bold")
                name_label.pack(fill = tk.X)
               
                # the contacts loyality is used to recolor the name ...
                loyality = float(contact.get("loyality","0"))
                if loyality >= 1: name_label.config(foreground = config.Colors.DARK_GREEN)
                if loyality < 0:  name_label.config(foreground = config.Colors.DARK_RED)
                if loyality > 0 and loyality <1: name_label.config(foreground = config.Colors.BLACK) 

                # display the characters competency ...
                competency = contact.get("competency","") + " (" + contact.get("competencylevel","") + ")"
                competency_label = tk.Label(box,text = competency, font = "Arial 9 bold")
                competency_label.pack()

                # ... and the current known location 
                location = contact.get("location","")
                location_label = tk.Label(box,text = location, font = "Arial 9 italic")
                location_label.pack()

                # draw box to canvas
                canvas.create_window(col * width,  # x
                                     row * height, # y
                                     window = box, 
                                     width = width, 
                                     height = height, 
                                     anchor = tk.NW)
                
                # bind the whole stuff to one command ... 
                for widget in (box, name_label, competency_label, location_label):
                    widget.bind("<Button-1>",lambda event, id = id: self.editContact(event,id))
                
                # set grid location for next box ...                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1

        # finally add a button to add contacts ... 
        new_button = tk.Button(canvas, text = "+", 
                               foreground = "#cccccc",
                               font = "Arial 40 bold", 
                               relief = tk.RIDGE, 
                               command = self.newContact)
        canvas.create_window(col * width,  # x
                             row * height, # y
                             window = new_button, 
                             width = width, 
                             height = height, 
                             anchor = tk.NW)

    # add new contact to character and load it in editor ...
    def newContact(self):
        new_id = self.char.newContact("")
        contact = self.char.getContactById(new_id)
        self.displaySocialEditor(contact)

    def editContact(self,event,id):
        contact = self.char.getContactById(id)
        self.displaySocialEditor(contact)

    # called to open a contact
    def displaySocialEditor(self,contact):
        if self.app.open_windows["contact"] == 0:
            SocialEditor(self, contact)
        else: 
            self.app.open_windows["contact"].close()
            SocialEditor(self, contact)
