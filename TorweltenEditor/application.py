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
from aboutscreen import About
from improvewindow import Improve
from PIL import ImageTk, Image, PngImagePlugin
import tk_ as tk

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
        main.title(msg.TITLE)
        self.style = tk.Style()
        self._setStyle()

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
            label=msg.MENU_EWT,
            command=lambda: self._switchWindow(msg.MENU_EWT)
        )
        self.toolmenu.add_command(
            label=msg.MENU_IMPROVE, 
            command=self._displayImprove
        )
        self.toolmenu.add_command(
            label=msg.MENU_SETTINGS,
            command=lambda: self._switchWindow(msg.MENU_SETTINGS)
        )
        self.toolmenu.add_command(
            label=msg.MENU_RELOAD_DATA,
            command=self._reloadData
        )
        self.toolmenu.add_command(
            label=msg.MENU_CHAR_LOG,
            command=lambda: self._switchWindow(msg.MENU_CHAR_LOG)
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
        self.columnconfigure(0, weight=100)

        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=1, sticky="nw")

        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, sticky="sw")

        self.toolbar = tk.Frame(self)
        self.toolbar.grid(row=0, sticky="we")

        self.rowconfigure(1, weight=1000)

        # self.startScreenImage()
        self.newChar()
        self.showToolbar()

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
        width = 20

        for i, label in enumerate(buttons):
            image = ImageTk.PhotoImage(file=label[1])
            button = tk.Button(
                self.toolbar,
                width=width,
                text=label[0],
                image=image,
                compound=tk.TOP
            )
            button.image = image
            button.config(
                command=lambda label=label[0]:
                self._switchWindow(label)
            )
            button.grid(row=0, column=i, sticky=tk.EW)

    def newChar(self):
        """ Creating a new empty character template """
        self.char = Character()
        init_xp = int(self.settings.getInitialXP())
        self.char.addXP(
            amount=init_xp,
            reason=msg.CHAR_INITIAL_XP
        )
        self._switchWindow(msg.TOOLBAR_CHAR_DATA)
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
            self.char.load(filename)

            self._switchWindow(msg.TOOLBAR_CHAR_DATA)
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

    def _switchWindow(self, label):

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
        }

        # display the new module
        window = ProgramModule[label](frame, app=self)
        window.pack()

    def _displayImprove(self):
        window = Improve(self)

    def about(self):
        self._switchWindow(msg.MENU_ABOUT)

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
        self._switchWindow(msg.TOOLBAR_CHAR_DATA)

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
