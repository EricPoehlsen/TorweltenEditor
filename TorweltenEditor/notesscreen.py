import tk_ as tk
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
        self.style = app.style
        self.app = app
        self.char = app.char
        self.open_windows = app.open_windows
        self.unlocked = -1

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
        ToolTip(new_note, msg.NS_TT_NEW)
        if self.char.getEditMode() != "view":
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
        )
        delete_button.bind(
            "<Button-1>",
            lambda event, id=id: self._delNote(event, id))
        ToolTip(delete_button, msg.NS_TT_DELETE)
        delete_button.image = del_icon
        delete_button.pack(side=tk.LEFT, fill=tk.BOTH)

        title_frame.pack(padx=2, pady=2, fill=tk.X, expand=1)
        text_widget = tk.Text(
            frame,
            width=20,
            height=12,
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#666666",
            font="Arial 10"
        )
        text_widget.insert("0.0", text)
        text_widget.bind("<FocusOut>", update)
        text_widget.bind("<space>", update)
        text_widget.bind("<Return>", update)
        text_widget.bind("<Tab>", update)

        text_widget.pack(padx=2, fill=tk.X)

        if self.char.getEditMode() == "view":
            title.state(["disabled"])
            delete_button.state(["disabled"])
            text_widget.config(
                state=tk.DISABLED,
                background="#eeeeee",
                borderwidth=0,
                highlightthickness=1,
                highlightbackground="#cccccc",
            )

        height = title.winfo_reqheight() + text_widget.winfo_reqheight()

        return frame, height

    def _delNote(self, event, id):
        if id == self.unlocked:
            self.char.delNote(id)
            self.showNotes(self.notes_canvas)
            self.unlocked = -1
        else:
            self.unlocked = id
            event.widget.config(style="destroy.TButton")

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
