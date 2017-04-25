import tk_ as tk
import tkinter.messagebox as tkmb
from PIL import ImageTk
import config
from tooltip import ToolTip

msg = config.Messages()


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

        self.elements = 3
        self.height = 200

        # create canvas ... 
        self.notes_canvas = tk.Canvas(self, width=1, height=1)
        self.notes_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.notes_scroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.notes_scroll.pack(side=tk.LEFT, fill=tk.Y) 
        self.notes_scroll.config(command=self.notes_canvas.yview)
        self.notes_canvas.config(yscrollcommand=self.notes_scroll.set)
        self.notes_canvas.bind("<Configure>", self.resize)
        self.showNotes(self.notes_canvas)

    def resize(self, event):
        w = event.width
        old_elements = self.elements
        self.elements = w // 250

        if self.elements != old_elements:
            self.showNotes(self.notes_canvas)

    # show all contacts
    def showNotes(self, canvas):
        """ display all contacts 
        
        canvas (tk.Canvas): the canvas to draw on 
        """

        # clear canvas
        canvas.delete("all")
        # prepare layouting variables
        row = 0
        col = 0
        width = canvas.winfo_width()

        # retrieve notes
        notes = self.char.getNotes()
        for note in notes:
            frame = self.noteFrame(note)

            x = col * width/self.elements,
            y = row * self.height,

            canvas.create_window(
                x,
                y,
                width=width/self.elements,
                height=self.height,
                anchor=tk.NW,
                window=frame
            )

            col += 1
            if col >= self.elements:
                col = 0
                row += 1

        if self.char.getEditMode() != "view":
            new_icon = ImageTk.PhotoImage(file="img/note_add.png")
            new_note = tk.Button(
                canvas,
                width=width/self.elements,
                height=self.height,
                image=new_icon,
                command=self.addNote
            )
            new_note.image = new_icon
            ToolTip(new_note, msg.NS_TT_NEW)

            x = col * width/self.elements,
            y = row * self.height,

            canvas.create_window(
                x,
                y,
                width=width / self.elements,
                height=self.height,
                anchor=tk.NW,
                window=new_note
            )

        self.notes_canvas.config(
            scrollregion=(0, 0, 1, (row+1)*self.height)
        )

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
        title = tk.Entry(frame, width=15, font="Arial 14 bold")
        title.insert("0", name)
        title.bind("<KeyRelease>", update)
        title.place(
            x=0,
            y=0,
            relheight=.1,
            relwidth=.9,
            anchor=tk.NW
        )

        del_icon = ImageTk.PhotoImage(file="img/cross_small.png")
        delete_button = tk.Button(
            frame,
            image=del_icon,
        )
        delete_button.bind(
            "<Button-1>",
            lambda event, id=id: self._delNote(event, id))
        ToolTip(delete_button, msg.NS_TT_DELETE)
        delete_button.image = del_icon
        delete_button.place(
            relx=1,
            y=0,
            relheight=.1,
            relwidth=.1,
            anchor=tk.NE
        )
        text_widget = tk.Text(
            frame,
            width=1,
            height=1,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#666666",
            font="Arial 10"
        )
        text_widget.insert("0.0", text)
        text_widget.bind("<KeyRelease>", update)

        text_widget.place(
            relx=0,
            rely=.1,
            relheight=.9,
            relwidth=1,
            anchor=tk.NW
        )

        if self.char.getEditMode() == "view":
            title.config(state=tk.DISABLED)
            delete_button.config(state=tk.DISABLED)
            text_widget.config(
                state=tk.DISABLED,
                background="#eeeeee",
                borderwidth=0,
                highlightthickness=1,
                highlightbackground="#cccccc",
            )

        return frame

    def _delNote(self, event, id):
        note = self.char.findNoteById(id)
        name = note.get("name")
        text = msg.NS_DEL_TEXT
        if name:
            text = text.format(name="'" + name + "' ")
        else:
            text = text.format(name="")

        delete = tkmb.askyesno(
            msg.NS_DEL_TITLE,
            text,
            parent=self,
            icon=tkmb.WARNING
        )

        if delete:
            self.char.delNote(id)
            self.showNotes(self.notes_canvas)
            self.unlocked = -1

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
