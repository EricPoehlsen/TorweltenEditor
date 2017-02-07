import re
import tkinter.filedialog as tkfd
import char_xml as character
import item_xml
import skill_xml
import trait_xml
import config
from charscreen import CharScreen
from traitselector import TraitSelector
from traitinfo import TraitInfo
from equipmentscreen import EquipmentScreen
from ewtscreen import EWTScreen
from socialscreen import SocialScreen
from settingscreen import SettingScreen
from logscreen import LogScreen
from sheetlayoutscreen import LayoutScreen
from exportpdf import ExportPdf
from imagescreen import ImageScreen
from improvewindow import Improve
from PIL import ImageTk,Image,PngImagePlugin
import tkinter as tk

msg = config.Messages()


class Application(tk.Frame):
    """ The applications main window layout

    within this you find the primary screen layout
    the calls to other windows and the definition of
    the menus.
    """

    def __init__(self, main):
        tk.Frame.__init__(self, main)
        # maybe important later ... 
        self.dimensions = None
        
        # create the character instance # #
        self.char = character.Character()
        self.skills = skill_xml.SkillTree()
        self.traits = trait_xml.TraitTree()
        self.itemlist = item_xml.ItemTree()

        self.main = main
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
        self.toolbar = tk.Frame(self)
        self.toolbar.grid(row=0, sticky="nw")

        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=1, sticky="nw")

        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, sticky="sw")

        self.main.rowconfigure(1, weight=1000)

        self.newChar()
        self.showToolbar()

    def showToolbar(self):
        """ Rendering the toolbar """

        buttons = [
            msg.TOOLBAR_CHAR_DATA,
            msg.TOOLBAR_CHAR_EQUIP,
            msg.TOOLBAR_CHAR_CONTACTS,
            msg.TOOLBAR_CHAR_IMAGE,
            msg.TOOLBAR_CHAR_LAYOUT
        ]

        for button_label in buttons:
            button = tk.Button(self.toolbar, text=button_label)
            button.config(
                command=lambda label=button_label:
                self._switchWindow(label)
            )
            button.pack(side=tk.LEFT)

    def newChar(self):
        """ Creating a new empty character template """
        self.char = character.Character()
        self.char.addXP(
            amount=300, 
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
        for widget in widgets: widget.destroy()

    def _switchWindow(self, label):

        """ switching program modules

         Args:
             label (str): text on the widget calling the command ...
        """

        self._clearMainFrame()
        frame = self.main_frame
        # the program modules...
        ProgramModule = {
            msg.TOOLBAR_CHAR_DATA: CharScreen,
            msg.TOOLBAR_CHAR_EQUIP: EquipmentScreen,
            msg.TOOLBAR_CHAR_CONTACTS: SocialScreen,
            msg.TOOLBAR_CHAR_IMAGE: ImageScreen,
            msg.TOOLBAR_CHAR_LAYOUT: LayoutScreen,
            msg.MENU_SETTINGS: SettingScreen,
            msg.MENU_EWT: EWTScreen,
            msg.MENU_CHAR_LOG: LogScreen}

        window = ProgramModule[label](frame, app=self)
        window.pack()
                    
    def showTraitInfo(self, event):
        window = TraitInfo(self, event)

    def _displayImprove(self):
        window = Improve(self)

    def about(self):
        print("About")

    # TODO this is a currently unused
    def startScreenImage(self):
        photo = ImageTk.PhotoImage(file="logo.png")
        label = tk.Label(self.main_frame, image = photo)
        label.image = photo
        label.pack()
        
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
        
    def _reloadData(self):
        """ Reloading data files

        called by menu entry or hotkey
        """

        self.itemlist.loadTree()
        self.skills.loadTree()
        self.traits.loadTree()

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
