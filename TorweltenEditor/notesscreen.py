# coding=utf-8
import tkinter as tk
from PIL import ImageTk
import config


class NotesScreen(tk.Frame):
    """ The notes screen displays and modifies character notes ... 

    main (tk.Tk): holding the program
    app (Application): the programs primary screen 
    """

    def __init__(self, main, app):
        tk.Frame.__init__(self,main)
        self.app = app
        self.char = app.char
        self.open_windows = app.open_windows

        self.notes = {}

        # create canvas ... 
        self.notes_canvas = tk.Canvas(self, width=770, height=540)
        self.notes_canvas.pack(side = tk.LEFT)
        self.notes_scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.notes_scroll.pack(side=tk.LEFT, fill=tk.Y) 
        self.notes_scroll.config(command=self.notes_canvas.yview)
        self.notes_canvas.config(yscrollcommand=self.notes_scroll.set)

        self.showNotes(self.notes_canvas)

    # show all contacts
    def showNotes(self, canvas):
        """ display all contacts 
        
        canvas (tk.Canvas): the canvas to draw on 
        """

        # clear canvas
        canvas.delete(tk.ALL)

        # prepare layouting variables
        row = 0
        col = 0
        width = canvas.winfo_reqwidth()//3 - 8
        height = 0

        # retrieve notes
        notes = self.char.getNotes()
        for note in notes:
            element, h = self.noteFrame(note)
            if not height:
                height = h + 6

            x = col * (width + 4) + 4
            y = row * height
            self.notes_canvas.create_window(
                x,
                y,
                width=width,
                anchor=tk.NW,
                window=element,
            )

            col += 1
            if col == 3:
                col = 0
                row += 1

        x = col * (width + 4) + 4
        y = row * height

        new_icon = ImageTk.PhotoImage(file="img/note_add.png")
        new_note = tk.Button(
            canvas,
            image=new_icon,
            command=self.addNote
        )
        new_note.image = new_icon
        canvas.create_window(
            x,
            y,
            width=64,
            height=64,
            window=new_note,
            anchor=tk.NW,
        )

        self.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def addNote(self):
        self.char.addNote()
        self.showNotes(self.notes_canvas)

    def noteFrame(self, note):

        id = note.get("id", "")
        name = note.get("name", "")
        update = lambda event, id=id: self._update(event, id)
        text = note.text
        if not text:
            text = ""
        frame = tk.Frame(self.notes_canvas)
        title_frame = tk.Frame(frame)
        title = tk.Entry(title_frame, width=15, font="Arial 14 bold")
        title.insert("0", name)
        title.bind("<FocusOut>", update)
        title.bind("<Return>", update)
        title.bind("<Tab>", update)

        title.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        del_icon = ImageTk.PhotoImage(file="img/cross_small.png")
        delete_button = tk.Button(
            title_frame,
            image=del_icon,
            command=lambda id=id: self._delNote(id),
            state=tk.DISABLED
        )
        delete_button.bind("<Button-1>", self._unlockDelete)
        delete_button.image = del_icon
        delete_button.pack(side=tk.LEFT)

        title_frame.pack(fill=tk.X, expand=1)

        text_widget = tk.Text(
            frame,
            width=20,
            height=12,
            wrap=tk.WORD,
            font="Arial 10"
        )
        text_widget.insert("0.0", text)
        text_widget.bind("<FocusOut>", update)
        text_widget.bind("<space>", update)
        text_widget.bind("<Return>", update)
        text_widget.bind("<Tab>", update)

        text_widget.pack(fill=tk.X)

        height = title.winfo_reqheight() + text_widget.winfo_reqheight()

        return frame, height

    def _unlockDelete(self, event):
        widget = event.widget
        def unlock(widget):
            widget.config(state=tk.NORMAL)

        widget.after(500, lambda widget=widget: unlock(widget))

    def _delNote(self, id):
        self.char.delNote(id)
        self.showNotes(self.notes_canvas)

    def _update(self, event=None, id=""):
        text = ""
        name = ""
        if event:
            if type(event.widget) == tk.Text:
                text = event.widget.get("0.0", tk.END)
            else:
                name = event.widget.get()

        note = self.char.findNoteById(id)

        if note is not None:
            if text:
                note.text = text
            if name:
                note.set("name", name)
