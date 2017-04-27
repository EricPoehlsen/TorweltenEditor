import re
import tkinter.filedialog as tkfd
from setting_xml import Settings
from char_xml import Character
from item_xml import ItemTree
from skill_xml import SkillTree
from trait_xml import TraitTree
import config
from charscreen import CharScreen
from equipmentscreen import EquipmentScreen
from ewtscreen import EWTScreen
from socialscreen import SocialScreen
from settingscreen import SettingScreen
from logscreen import LogScreen
from sheetlayoutscreen import LayoutScreen
from exportpdf import ExportPdf
from imagescreen import ImageScreen
from notesscreen import NotesScreen
from expansionscreen import ExpansionScreen
from aboutscreen import About
from improvewindow import Improve
from PIL import ImageTk, Image, PngImagePlugin
import tk_ as tk
import tkinter.messagebox as tkmb

msg = config.Messages()


class Application(tk.Frame):
    """ The applications main window layout

    within this you find the primary screen layout
    the calls to other windows and the definition of
    the menus.
    """

    def __init__(self, main):
        tk.Frame.__init__(self, main)
        self.main = main

        self.module = None

        # setting up data
        self.settings = Settings()

        self.char = Character()
        self.skills = SkillTree(self.settings)
        self.traits = TraitTree(self.settings)
        self.itemlist = ItemTree(self.settings)

        self._setHotkeys()

        # creating the menu
        self.menubar = tk.Menu(main)
        # building the file menu
        self.filemenu = tk.Menu(self.menubar, tearoff="0")
        self.filemenu.add_command(
            label=msg.MENU_NEW,
            command=self.newChar
        )
        self.filemenu.add_command(
            label=msg.MENU_LOAD,
            command=self.openCharWindow
        )
        self.filemenu.add_command(
            label=msg.MENU_SAVE,
            command=self.saveCharWindow
        )
        self.filemenu.add_command(
            label=msg.MENU_PDFEXPORT,
            command=self.exportCharWindow
        )
        self.filemenu.add_command(
            label=msg.MENU_QUIT,
            command=self.main.destroy
        )
        self.menubar.add_cascade(
            label=msg.MENU_FILE,
            menu=self.filemenu
        )

        # building the tools menu
        self.toolmenu = tk.Menu(self.menubar, tearoff="0")
        self.toolmenu.add_command(
            label=msg.MENU_EDITMODE,
            command=self._editModeWindow
        )
        self.toolmenu.add_command(
            label=msg.MENU_EWT,
            command=lambda: self.switchWindow(msg.MENU_EWT)
        )
        self.toolmenu.add_command(
            label=msg.MENU_IMPROVE, 
            command=self._displayImprove
        )
        self.toolmenu.add_command(
            label=msg.MENU_SETTINGS,
            command=lambda: self.switchWindow(msg.MENU_SETTINGS)
        )
        self.toolmenu.add_command(
            label=msg.MENU_RELOAD_DATA,
            command=self._reloadData
        )
        self.toolmenu.add_command(
            label=msg.MENU_CHAR_LOG,
            command=lambda: self.switchWindow(msg.MENU_CHAR_LOG)
        )
        self.toolmenu.add_command(
            label=msg.MENU_EDIT_EXPANSION,
            command=lambda: self.switchWindow(msg.MENU_EDIT_EXPANSION)
        )
        self.menubar.add_cascade(
            label=msg.MENU_TOOLS,
            menu=self.toolmenu
        )

        # building the help menu
        self.helpmenu = tk.Menu(self.menubar, tearoff="0")
        self.helpmenu.add_command(
            label=msg.MENU_ABOUT,
            command=self.about
        )
        self.menubar.add_cascade(
            label=msg.MENU_HELP,
            menu=self.helpmenu
        )

        # assigning the menu ...
        main.config(menu=self.menubar)

        # stuff that needs to be available across some functions
        self.global_vars = {}

        # defining a dict for subwindows to track them
        self.open_windows = {
            "trait": 0,
            "skill": 0,
            "inv": 0,
            "contact": 0,
            "itemedit": 0,
            "mod_ed": 0,
            "improve": 0
        }

        self.widgets = {}

        # initializing the basic screen layout ...
        self.toolbar = tk.Frame(self)
        self.toolbar.place(
            x=0,
            y=0,
            relheight=.1,
            relwidth=1,
            anchor=tk.NW
        )

        self.main_frame = tk.Frame(self)
        self.main_frame.place(
            x=0,
            rely=.10,
            relheight=.85,
            relwidth=1,
            anchor=tk.NW
        )
        self.status_bar = StatusBar(self)
        self.status_bar.place(
            x=0,
            rely=1,
            relheight=.05,
            relwidth=1,
            anchor=tk.SW
        )

        # self.startScreenImage()
        self.newChar()
        self.showToolbar()
        self.updateTitle()
        self.size = (
            self.winfo_toplevel().winfo_reqwidth(),
            self.winfo_toplevel().winfo_reqheight()
        )

    def showToolbar(self):
        """ Rendering the toolbar """

        buttons = [
            (msg.TOOLBAR_CHAR_DATA, "img/data.png"),
            (msg.TOOLBAR_CHAR_EQUIP, "img/backpack.png"),
            (msg.TOOLBAR_CHAR_CONTACTS, "img/contacts.png"),
            (msg.TOOLBAR_CHAR_NOTES, "img/note.png"),
            (msg.TOOLBAR_CHAR_IMAGE, "img/char_image.png"),
            (msg.TOOLBAR_CHAR_LAYOUT, "img/pdf.png")
        ]

        for i, label in enumerate(buttons):
            image = ImageTk.PhotoImage(file=label[1])
            button = tk.Button(
                self.toolbar,
                text=label[0],
                image=image,
                compound=tk.TOP
            )
            button.image = image
            button.config(
                command=lambda label=label[0]:
                self.switchWindow(label)
            )
            button.place(
                relx=i/6,
                relwidth=1/6,
                x=0,
                relheight=1
            )

    def newChar(self):
        """ Creating a new empty character template """
        self.char = Character()
        init_xp = int(self.settings.getInitialXP())
        self.char.addXP(
            amount=init_xp,
            reason=msg.CHAR_INITIAL_XP
        )
        self.switchWindow(msg.TOOLBAR_CHAR_DATA)
        self.status_bar.rebind(self)
    
    def openCharWindow(self):
        """ File open dialog => open character """

        options = {
            'defaultextension': '.xml',
            'filetypes': [('Charakterdateien', '.xml')],
            'initialdir': './chars',
            'initialfile': 'character.xml',
            'parent': self.main,
            'title': 'Charakter laden ...',
            }
        filename = tkfd.askopenfilename(**options)
        if filename:
            error = self.char.load(filename)
            if error:
                errors = {
                    -1: msg.ERROR_XML_UNKNOWN,
                    1: msg.ERROR_XML_PARSE,
                    2: msg.ERROR_XML_NO_CHAR
                }
                tkmb.showerror(msg.ERROR, errors[error], parent=self)

            self.switchWindow(msg.TOOLBAR_CHAR_DATA)
            self.status_bar.rebind(self)
        else:
            pass

    def saveCharWindow(self):
        """ File save dialog => stores current character to disk """

        suggested_filename = "character.xml"
        charname = self.char.getData("name")
        if len(charname) > 0:
            regex = "[^a-zA-Z0-9\xE4\xF6\xFC\xC4\xD6\xDC\xDF]"
            suggested_filename = re.subn(regex, "_", charname)[0]+".xml"

        options = {
            'defaultextension': '.xml',
            'filetypes': [('Charakterdateien', '.xml')],
            'initialdir': './chars',
            'initialfile': suggested_filename,
            'parent': self.main,
            'title': 'Charakter speichern ...',
            }
        filename = tkfd.asksaveasfilename(**options)
        if filename:
            self.char.save(filename)

    def exportCharWindow(self, template=None):
        """ File save dialog => PDF export to disk """

        suggested_filename = "character.pdf"
        charname = self.char.getData("name")
        if len(charname) > 0:
            regex = "[^a-zA-Z0-9\xE4\xF6\xFC\xC4\xD6\xDC\xDF]"
            suggested_filename = re.subn(regex, "_", charname)[0]+".pdf"
            
        options = {
            'defaultextension': '.pdf',
            'filetypes': [('PDF Dokument', '.pdf')],
            'initialdir': './chars',
            'initialfile': suggested_filename,
            'parent': self.main,
            'title': 'Charakter speichern ...'
            }
        filename = tkfd.asksaveasfilename(**options)
        
        if len(filename) > 0:
            ExportPdf(filename, self.char, self.traits, template)

    def _clearMainFrame(self):
        """ destroying all children in self.main_frame """

        widgets = self.main_frame.winfo_children()
        for widget in widgets:
            widget.destroy()

    def switchWindow(self, label):

        """ switching program modules

         Args:
             label (str): text on the widget calling the command ...
        """

        # make sure all open windows are closed ...
        for mod_name in self.open_windows:
            if self.open_windows[mod_name] != 0:
                self.open_windows[mod_name].close()

        # prepare the frame
        self._clearMainFrame()
        frame = self.main_frame

        # the program modules...
        ProgramModule = {
            msg.TOOLBAR_CHAR_DATA: CharScreen,
            msg.TOOLBAR_CHAR_EQUIP: EquipmentScreen,
            msg.TOOLBAR_CHAR_CONTACTS: SocialScreen,
            msg.TOOLBAR_CHAR_IMAGE: ImageScreen,
            msg.TOOLBAR_CHAR_LAYOUT: LayoutScreen,
            msg.TOOLBAR_CHAR_NOTES: NotesScreen,
            msg.MENU_SETTINGS: SettingScreen,
            msg.MENU_EWT: EWTScreen,
            msg.MENU_CHAR_LOG: LogScreen,
            msg.MENU_ABOUT: About,
            msg.MENU_EDIT_EXPANSION: ExpansionScreen,
        }

        # display the new module
        self.module = ProgramModule[label](frame, app=self)
        self.module.place(x=0,y=0,relwidth=1,relheight=1,anchor=tk.NW)

    def _displayImprove(self):
        window = Improve(self)

    def about(self):
        self.switchWindow(msg.MENU_ABOUT)

    # TODO this is a currently unused
    def startScreenImage(self):

        photo = ImageTk.PhotoImage(file="img/logo.png")
        label = tk.Label(self.main_frame, image=photo)
        label.image = photo
        label.pack()

    def _setStyle(self):
        self.style.configure(
            "red.TLabel",
            foreground = config.Colors.DARK_RED
        )
        self.style.configure(
            "green.TLabel",
            foreground=config.Colors.DARK_GREEN
        )
        self.style.configure(
            "attr.TLabel",
            font="Arial 14 bold",
            justify=tk.CENTER,
            anchor=tk.CENTER

        )

        self.style.configure(
            "test.TFrame",
            background = "#ff0000"
        )
        self.style.configure(
            "selected.TButton",
            foreground="#000000",
            font="Arial 10 bold"
        )

        self.style.configure(
            "destroy.TButton",
            background="#ff0000",
            foreground="#ff0000"
        )

        self.style.configure(
            "invalid.TEntry",
            foreground="#ff0000",

        )

        # edit_entry - editable labels for the itemeditor
        self.style.layout(
            "edit_entry",
            [('edit_entry', {'sticky': 'nswe', 'children':
                [('Entry.background', {'sticky': 'nswe', 'children':
                    [('Entry.padding', {'sticky': 'nswe', 'children':
                        [('Entry.textarea', {'sticky': 'nswe'})]}
                    )]}
                )]}
            )]
        )
        self.style.map(
            "edit_entry",
            foreground=[("active", "#000000"), ("disabled", "#000000")],
            background=[("active", "#ffffff"), ("disabled", "#eeeeee")],
            borderwidth=[("active", 0), ("disabled", 0)],
        )

    def _setHotkeys(self):
        """ Binding global hotkeys """

        self.main.bind_all(
            "<Control-n>",
            lambda event: self.newChar()
        )
        self.main.bind_all(
            "<Control-s>",
            lambda event: self.saveCharWindow()
        )
        self.main.bind_all(
            "<Control-o>",
            lambda event: self.openCharWindow()
        )
        self.main.bind_all(
            "<Control-F5>",
            lambda event: self._reloadData()
        )
        self.main.bind_all(
            "<F9>",
            lambda event: self._switchEditMode("generation")
        )
        self.main.bind_all(
            "<F10>",
            lambda event: self._switchEditMode("edit")
        )
        self.main.bind_all(
            "<F11>",
            lambda event: self._switchEditMode("simulation")
        )
        self.main.bind_all(
            "<F12>",
            lambda event: self._switchEditMode("view")
        )

    def _switchEditMode(self, mode):
        self.char.setEditMode(mode)
        self.updateTitle()
        self.switchWindow(msg.TOOLBAR_CHAR_DATA)

    def updateTitle(self):
        modes = {
                "generation": msg.TITLE_EM_GENERATION,
                "edit": msg.TITLE_EM_EDIT,
                "view": msg.TITLE_EM_VIEW,
                "simulation": msg.TITLE_EM_SIMULATION,
            }

        title = [
            msg.TITLE,
            self.char.getData("name"),
            modes.get(self.char.getEditMode(), "")
        ]
        title = " - ".join(title)
        self.main.title(title)

    def _reloadData(self):
        """ Reloading data files

        called by menu entry or hotkey
        """

        self.itemlist.buildTree()
        self.skills.buildTree()
        self.traits.buildTree()

    # this will later be used to prepare the screen for high resolution screens
    def _resolution(self):
        width = self.main.winfo_screenwidth()
        height = self.main.winfo_screenheight()
        width_mm = self.main.winfo_screenmmwidth() 
        height_mm = self.main.winfo_screenmmheight()

        width_in = width_mm / 25.4
        height_in = height_mm / 25.4
        
        dpi = (width/width_in,height/height_in)
        print(dpi)

    def _editModeWindow(self):
        window = EditModeSwitcher(self)


class StatusBar(tk.Frame):
    """ the status bar displays some information across all modules """

    def __init__(self, main):
        tk.Frame.__init__(self, main)
        self.char = main.char
        self.xp_label = tk.Label(
            self,
            text="XP verfügbar: "
            )
        self.xp_label.pack(side=tk.LEFT)
        self.xp_info = tk.Label(
            self, 
            anchor=tk.W, 
            textvariable=self.char.xp_avail
            )
        self.xp_info.pack(side=tk.LEFT)
        self.money_label = tk.Label(
            self, 
            text="| Geld verfügbar: "
            )
        self.money_label.pack(side=tk.LEFT)
        self.money_info = tk.Label(
            self, 
            textvariable=self.char.account_balance
            )
        self.money_info.pack(side=tk.LEFT)
        self.freeMode()

    def freeMode(self):
        print("free mode")
        print(self.char.getData("name"))
        if self.char.getFreeXP():
            self.xp_info.config(**config.Style.STATUSBAR_FREE)
            self.xp_label.config(**config.Style.STATUSBAR_FREE)
        else:
            self.xp_info.config(**config.Style.STATUSBAR_NORMAL)
            self.xp_label.config(**config.Style.STATUSBAR_NORMAL)

        if self.char.getFreeMoney():
            self.money_info.config(**config.Style.STATUSBAR_FREE)
            self.money_label.config(**config.Style.STATUSBAR_FREE)
        else:
            self.money_info.config(**config.Style.STATUSBAR_NORMAL)
            self.money_label.config(**config.Style.STATUSBAR_NORMAL)

    def rebind(self, app):
        """ Rebinding the status bar

        Note:
            After a new character is created or a character is loaded
            the status bar need to be rebound to the character variables

        Args:
            app (Application): the main application instance

            """

        self.xp_info.config(textvariable=app.char.xp_avail)
        self.money_info.config(textvariable=app.char.account_balance)
        self.char = app.char


class EditModeSwitcher(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.wm_protocol("WM_DELETE_WINDOW", self.close)
        self.char = master.char
        self.data = {}
        editmode = self.editModeSwitcher(self)
        editmode.pack(fill=tk.BOTH, expand=1)

        freemode = self.freeModeSwitcher(self)
        freemode.pack(fill=tk.BOTH, expand=1)

        switch = tk.Button(
            self,
            text=msg.SET_EDIT_SWITCH,
            command=self.setEditMode
        )
        switch.pack(fill=tk.X)

    def editModeSwitcher(self, parent):
        var = self.data["editmode"] = tk.StringVar()

        frame = tk.LabelFrame(parent, text=msg.SET_EDIT_MODE)
        modes = [
            (msg.SET_EDIT_GENERATION, "generation"),
            (msg.SET_EDIT_EDIT, "edit"),
            (msg.SET_EDIT_VIEW, "view"),
            (msg.SET_EDIT_SIM, "simulation")
        ]
        for txt, val in modes:
            button = tk.Radiobutton(
                frame,
                text=txt,
                variable=var,
                value=val,
            )
            button.deselect()
            button.pack(anchor=tk.W)

        var.set(self.char.getEditMode())

        return frame

    def freeModeSwitcher(self, parent):
        free_xp = self.data["free_xp"] = tk.IntVar()
        if self.char.getFreeXP(): free_xp.set(1)
        free_money = self.data["free_money"] = tk.IntVar()
        if self.char.getFreeMoney(): free_money.set(1)

        frame=tk.LabelFrame(parent, text=msg.SET_FREE_MODE)
        free_xp_button = tk.Checkbutton(
            frame,
            text=msg.SET_FREE_XP,
            variable=free_xp,
            onvalue=1,
            offvalue=0
        )
        free_xp_button.pack()
        free_money_button = tk.Checkbutton(
            frame,
            text=msg.SET_FREE_MONEY,
            variable=free_money,
            onvalue=1,
            offvalue=0
        )
        free_money_button.pack()
        return frame

    def setEditMode(self):
        mode = self.data["editmode"].get()
        free_xp = self.data["free_xp"].get()
        free_money = self.data["free_money"].get()
        self.char.setEditMode(mode, free_xp=free_xp, free_money=free_money)
        self.master.switchWindow(msg.TOOLBAR_CHAR_DATA)
        self.master.status_bar.freeMode()
        self.close()

    def close(self):
        self.destroy()
