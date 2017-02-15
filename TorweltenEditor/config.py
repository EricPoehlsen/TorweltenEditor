# coding=utf-8
"""
This file provides several classes containing constants. Some of these
constants may be retrieved from XML files ...
"""


#defining the EWT
#       -7  -6  -5  -4  -3  -2  -1   0   1   2   3   4   5   6   7 
EWT = [[2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0,1.0,1.0,1.0,1.0,0.5], #  1
       [2.0,2.0,2.0,2.0,2.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.0,0.0], #  2
       [2.0,2.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.0,0.0,0.0], #  3
       [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.0,0.0,0.0,0.0], #  4
       [1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0], #  5
       [1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0], #  6 
       [1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0], #  7
       [1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0], #  8
       [1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0], #  9
       [1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]] #  0



#THIS CLASS CONTAINS MESSAGES TO BE DISPLAYED ON THE UI OR PDF EXPORTS
class Messages:
    """ Messages provides a variety of strings for the UI and PDF Export
    WARNING: some strings are used as keys in dicts so make sure unicode
    strings are correctly defined otherwise you will be out of "Glück" ...
    """

    title = "Torwelten Charaktergenerator"

    # #####GENERIC UI TEXT # ######
    NAME = "Name"
    SPECIES = "Spezies"
    ORIGIN = "Herkunft"
    CONCEPT = "Konzept"
    PLAYER = "Spieler"
    HEIGHT = "Größe"
    WEIGHT = "Gewicht"
    AGE = "Alter"
    GENDER = "Geschlecht"
    HAIR = "Haarfarbe"
    EYES = "Augenfarbe"
    SKIN_COLOR = "Hautfarbe"
    SKIN_TYPE = "Hautart"
    XP = "XP"
    ITEMNAME = "Bezeichnung"

    MULTIPLY = "x"
    MONEYFORMAT = "%s,%s"
    DATEFORMAT = "%d.%m.%Y %H:%M:%S"

    # ##### MENU 
    # FILE MENU
    MENU_FILE = "Datei"
    MENU_NEW = "Neu ..."
    MENU_LOAD = "Charakter öffnen ..."
    MENU_SAVE = "Charakter speichern ..."
    MENU_PDFEXPORT = "PDF Export ..."
    MENU_QUIT = "Beenden"

    # TOOLS MENU
    MENU_TOOLS = "Werkzeuge"
    MENU_IMPROVE = "Charakter steigern ..."
    MENU_EWT = "EWT Tabelle"
    MENU_SETTINGS = "Einstellungen"
    MENU_RELOAD_DATA = "XMLs neu laden"
    MENU_CHAR_LOG = "Charakter Log"

    # HELP MENU
    MENU_HELP = "Hilfe"
    MENU_ABOUT = "About ..."

    # TOOLBAR
    TOOLBAR_CHAR_DATA = "Daten, Fertigkeiten, Eigenschaften"
    TOOLBAR_CHAR_EQUIP = "Ausrüstung und Waffen"
    TOOLBAR_CHAR_CONTACTS = "Soziales und Kontakte"
    TOOLBAR_CHAR_IMAGE = "Charakterbild"
    TOOLBAR_CHAR_LAYOUT = "Layout"

    # CHAR SCREEN
    CS_BASE_DATA = "Basisdaten"
    CS_TRAITS = "Vor- und Nachteile"
    CS_ADD_TRAIT = "Neue Eigenschaft ..."
    CS_ACTIVE_SKILLS = "Aktionsfertigkeiten"
    CS_PASSIVE_SKILLS = "Wissen und Sprachen"
    CS_ADD_SKILLS = "Fertigkeiten hinzufügen ..."

    # TRAIT SELECTOR
    TS_TITLE = "Eigenschaft hinzufügen"
    TS_SEARCH_NAME = "nach Name suchen ..."
    TS_NAME = "Name"
    TS_GROUP = "Gruppe"
    TS_CLASS = "Klasse"
    TS_SEARCH = "Suche"
    TS_TRAIT = "Eigenschaft"
    TS_DESCRIPTION = "Beschreibung ..."
    TS_ADD_TRAIT = "Ausgewählte Eigenschaft hinzufügen ..."
    TS_JUST_SCROLL = "einfach durchblättern..."

    # SKILL SELECTOR
    SS_TITLE = "Fertigkeiten wählen"
    SS_ADD_REMOVE_SKILLS = "Fertigkeiten hinzufügen/entfernen"
    SS_ADD_SKILLS = "Fertigkeiten hinzufügen"
    SS_ADD_SINGLE_SKILL = "Fertigkeit hinzufügen"
    SS_ADD_MULTIPLE_SKILLS = "{add} Fertigkeiten hinzufügen"
    SS_REMOVE_SINGLE_SKILL = "Fertigkeit entfernen"
    SS_REMOVE_MULTIPLE_SKILLS = "{rem} Fertigkeiten entfernen"
    SS_ADD_REMOVE_MULTIPLE_SKILLS = "Fertigkeiten: {add} hinzufügen, {rem} entfernen"
    SS_NEW_SKILL = "Eigene Fertigkeit hinzufügen ..."
    SS_SKILL_EXISTS = "Fertigkeit existiert bereits!"
    SS_ILLEGAL_CHARS = "Ungültige Zeichen im Namen!"
    SS_BASE = "[G]"
    SS_SPEC = "[S]"
    SS_SEARCH = "Suche"
    SS_X = " [X]"
    SS_TT_SHOW_BASE = "Grundfertigkeiten ein-\nund ausblenden: "
    SS_TT_SHOW_SPEC = "Spezialisierungen ein-\nund ausblenden: "
    SS_TT_SEARCH = "Fertigkeiten nach Name durchsuchen"
    SS_TT_NEWSKILL = "Eine eigene Fertigkeit oder\n" \
                     "Spezialisierung hinzufügen"
    SS_TT_NEW_DISABLED = "Um dieses Feld freizuschalten,\n" \
                         "zunächst eine Referenzfertigkeit\n" \
                         "auswählen ..."

    # SKILL INFO
    SI_SPEC1 = "ist eine Grundfertigkeit"
    SI_SPEC2 = "Fertigkeit in"
    SI_SPEC3 = "Spezialisierung in"
    SI_SPEC0 = "nicht zugeordnet"
    SI_OTHER_SPEC = "weitere Spezialisierungen"
    SI_CHILD_SPEC = "zugeordnete Spezialisierungen"
    SI_CHILD_SKILL = "zugeordnete Fertigkeiten"


    # EQUIPMENT SCREEN
    ES_BUY_BUTTON = "Ausrüstung beschaffen"
    ES_EQUIPPED = "Mitgeführte Ausrüstung"
    ES_MELEE = "Nahkampfwaffen"
    ES_GUNS = "Fernkampfwaffen"
    ES_UNASSIGNED = "Nicht zugewiesen"
    ES_INITIAL_FUNDS = "Startkapital: {amount},00 Rand"
    ES_CLOTHING_ARMOR = "Kleidung und Rüstung"
    ES_UNEQUIP = "Ablegen"
    ES_ITEMNAME = "Bezeichnung"
    ES_DAMAGE_S = "S / D"
    ES_QUALITY_S = "Q"
    ES_UNEQUIP_S = "A"
    ES_NOT_LOADED = "nicht geladen"
    ES_CHAMBERED_AMMO = "Kammern: {chambers} - davon geladen: {loaded}"
    ES_KG = " kg"
    ES_G = " g"
    ES_WEIGHT = "Gewicht: "
    ES_CLIP = "{name} - {number} / {capacity}"

    # ####ITEM EDITOR and INVENTORY EDITOR # ####
    IE_UNEQUIP = "Ablegen"
    IE_EQUIP = "Anlegen"
    IE_SPLIT = "Teilen"
    IE_CONDENSE = "Zusammenführen"
    IE_DESTROY = "Zerstören"
    IE_SELL = "Verkaufen"
    IE_KG = " kg"
    IE_G = " g"
    IE_WEIGHT = "Gewicht: "
    IE_CANCEL = "Abbrechen"
    IE_CONTENT = "Inhalt: "
    IE_CHAMBERS = "Kammern: "
    IE_EMPTY = "leer"
    IE_SHELL_CASING = "Patronenhülse"
    IE_FIRE_WEAPON = "Abfeuern"
    IE_CLEAR = "Leeren"
    IE_AVAILABLE_AMMO = "Verfügbare Munition"
    IE_LOADED = "Geladen ..."
    IE_NOT_LOADED = "Nicht geladen ..."
    IE_NO_CLIP_LOADED = "Kein Magazin eingelegt!"
    IE_CLIP_LOADED = "Eingelegtes Magazin:"
    IE_CLIP_STATUS = "Ladestand: "
    IE_EJECT = "Auswerfen"
    IE_CYCLE_WEAPON = "Durchladen"
    IE_COMPATIBLE_CLIPS = "Passende Magazine:"
    IE_LOAD_WEAPON = "Laden"
    IE_FILL_CLIP = "füllen"
    IE_ADD_ONE = "+1"
    IE_INSERT_CARTRIDGE = "Patrone einlegen ..."
    IE_QUALITY = "Qualität"
    IE_QUALITY_3 = "miserabel"
    IE_QUALITY_4 = "schlecht"
    IE_QUALITY_5 = "gebraucht"
    IE_QUALITY_6 = "standard"
    IE_QUALITY_7 = "gut"
    IE_QUALITY_8 = "sehr gut"
    IE_QUALITY_9 = "überragend"
    IE_TITLE = "Inventareditor"
    IE_AVAIL_S = "Verf."
    IE_COST = "Kosten"
    IE_BACK = "zurück"
    IE_QUANTITY = "Menge"
    IE_BUY = "Einkaufen"
    IE_PRICE = "Preis"
    IE_DAMAGE = "Schaden: {value}"
    IE_TYPE_CLOTHING = "Bekleidung oder Rüstung"
    IE_TYPE_MELEE = "Nahkampfwaffe"
    IE_TYPE_GUNS = "Fernkampfwaffe"
    IE_TYPE_CONTAINER = "Behälter",
    IE_TYPE_TOOLS = "Werkzeug",
    IE_TYPE_AMMO = "Munition",
    IE_TYPE_OTHER = "Sonstiges"
    IE_TYPE_UNDEFINED = "Bitte Typ wählen ..."
    IE_NAME = "Bezeichnung"
    IE_QUALITY_S = "Qual."
    IE_DAMAGE_HEADER = "Schadenswert: (benötigt für Waffen und Rüstung ...)"
    IE_USE = "verwenden"
    IE_CALIBER_HEAD = "Kaliber und Kammern (für Fernkampfwaffen ...)"
    IE_CALIBER = "Kaliber: "
    IE_CONTAINER = "Container (Taschen, Kisten, Behälter, ...)"
    IE_DESCRIPTION = "Beschreibung"
    IE_ADD_ITEM = "Gegenstand hinzufügen"
    IE_VALUE = "WERT!"
    IE_NUMBER = "ZAHL!"
    IE_INVALID = "UNGÜLTIG!"
    IE_NO_NAME = "NAME NOTWENDIG!"
    IE_CUSTOM_ITEM = "Neu ..."


    # IMPROVE WINDOW
    IW_TITLE = "Steigern ..."
    IW_EVENT = "Ereignis: "
    IW_MONEY = "Geldwerte Belohnung: "
    IW_AMOUNT = "Betrag:"
    IW_ACCOUNT = "Konto"
    IW_XP = "Erfahrungspunkte:"
    IW_CASH = "Bargeld"
    IW_ADD = "Ereignis hinzufügen"

    # ACOUNTS MANAGEMENT
    AC_PRIMARY_NAME = "Barvermögen [unspezifiziert]" #don't use () in this string!

    # SOCIAL EDITOR

    SE_CLOSE = "Schließen"
    SE_SAVE = "Speichern"
    SE_DELETE = "Löschen"
    SE_LOCATION = "Aufenthaltsort"
    SE_COMPETENCY = "Kompetenz"
    SE_LOYALITY = "Loyalität"
    SE_FREQUENCY = "Kontakthäufigkeit"
    SE_DESCRIPTION = "Beschreibung"

    SE_ENEMY_3 = "Erzfeind"
    SE_ENEMY_2 = "Feind"
    SE_ENEMY_1 = "Widersacher"
    SE_CONTACT = "rein geschäftlich"
    SE_FRIEND_1 = "Bekannter"
    SE_FRIEND_2 = "Freund"
    SE_FRIEND_3 = "Gefährte"

    SE_FREQUENCY_0 = "selten"
    SE_FREQUENCY_1 = "sporadisch"
    SE_FREQUENCY_2 = "gelegentlich"
    SE_FREQUENCY_3 = "regelmäßig"
    SE_FREQUENCY_4 = "häufig"
    SE_FREQUENCY_5 = "dauernd"



    # IMAGE SCREEN
    IS_ERROR = "Dateifehler!"
    IS_ERROR_TEXT = "Fehler beim Versuch die Datei %s zu laden."
    IS_ERROR_CLOSE = "Okay"
    IS_SET_SELECTION = "Ausschnitt festlegen"
    IS_IMPORT_IMAGE = "Bild importieren ..."
    IS_REMOVE_IMAGE = "Bild entfernen"
    IS_LOAD_IMAGE_TITLE = "Bilddatei laden ..."
    IS_LOAD_MIME = "Bilddateien ..."

    # for the sheetlayoutscreen
    SL_NEW = "Neu ..."
    SL_LOAD = "Laden ..."
    SL_SAVE = "Speichern ..."
    SL_EMPTY = "[ L E E R ]"
    SL_EXPORT = "PDF Exportieren"

    # for the module editor - moduleeditor.py 
    ME_NEW = "Neues Modul ..."
    ME_ADD = "Modul hinzufügen"
    ME_EDIT = "Modul bearbeiten..."
    ME_CHANGE_SIZE = "Größe ändern"
    ME_TEXTLINES = "Textzeilen"
    ME_SAVE = "Änderung speichern"
    ME_DELETE = "Modul löschen"
    ME_EQUIPPED_WEAPONS = "nur mitgeführte Waffen"
    ME_SHOW_QUANTITY = "Menge anzeigen"
    ME_CONDENSE = "Gegenstände zusammenfassen"
    ME_EQUIPPED_STUFF = "nur mitgeführte Ausrüstung"
    ME_BAG_CONTENTS = "Tascheninhalt anzeigen"
    ME_SHOW_WEAPONS = "Waffen anzeigen"
    ME_ONLY_BAG = "Nur den Inhalt der nachfolgend\n gewählten Tasche zeigen:"

    # for the pdf export - exportpdf.py and moduleeditor.py
    PDF_ATTRIBUTES = "Attribute"
    PDF_TRAITS = "Eigenschaften"
    PDF_ALL_TRAITS = "Vorteile und Nachteile"
    PDF_POSITIVE_TRAITS = "Vorteile"
    PDF_NEGATIVE_TRAITS = "Nachteile"
    PDF_SKILLS = "Fertigkeiten"
    PDF_SKILLS_ALL = "Alle Fertigkeiten"
    PDF_SKILLS_ACTIVE = "Aktionsfertigkeiten"
    PDF_SKILLS_PASSIVE = "Passive Fertigkeiten"
    PDF_SKILLS_KNOWLEDGE = "Wissensfertigkeiten"
    PDF_SKILLS_LANGUAGE = "Sprachfertigkeiten"
    PDF_EQUIPMENT = "Ausrüstung"
    PDF_WEAPONS = "Waffen"
    PDF_ALL_WEAPONS = "Alle Waffen"
    PDF_MELEE = "Nahkampfwaffen"
    PDF_GUNS = "Fernkampfwaffen"
    PDF_AMMO = "Munition"
    PDF_IMAGE = "Charakterbild"
    PDF_CONTACTS = "Kontakte"
    PDF_ALL_CONTACTS = "Alle Kontakte"
    PDF_FRIENDS = "Verbündete"
    PDF_ENEMIES = "Gegner"
    PDF_EWT = "EWT"
    PDF_NOTES = "Notizen"
    PDF_NAME_AND_INFO = "Bezeichnung & Info"
    PDF_SKILLNAME = "Fertigkeitsbezeichnung"
    PDF_CLOTHING_AND_MORE = "Kleidung & mehr"
    PDF_QUANTITY = "Menge"
    PDF_WEIGHT = "Gewicht"
    PDF_ITEMNAME = "Bezeichnung"
    PDF_DAMAGE = "S / D"
    PDF_CHAMBERS = "Kammern"
    PDF_CLIPSIZE = "-er Clip"
    PDF_CALIBER = "Kaliber"
    PDF_COMPENTECY = "Kompetenzbereich"
    PDF_COMP_LEVEL = "Fähigkeit"
    PDF_FREQUENCY = "Häufigkeit"
    PDF_LOYALITY = "Loyalität"
    PDF_FREQ_0 = "selten"
    PDF_FREQ_1 = "sporad."
    PDF_FREQ_2 = "geleg."
    PDF_FREQ_3 = "regelm."
    PDF_FREQ_4 = "häufig"
    PDF_FREQ_5 = "dauernd"
    PDF_EWT_TITLE = "Effektwerttabelle"

    PDF_SINGLE = "1x1 - klein"
    PDF_WIDE = "2x1 - breit"
    PDF_DOUBLE = "1x2 - doppelt"
    PDF_QUART = "2x2 - Viertelseite"
    PDF_TRIPLE = "1x3 - dreifach"
    PDF_BIG = "2x3 - groß"
    PDF_FULL = "1x4 - ganze Spalte"
    PDF_HALF = "2x4 - halbe Seite"
    PDF_ATTRIB_IMAGE = "im Attributsmodul"

    # these strings are used in the character xml 
    CHAR_CREATED = "Charaktergenerierung gestartet ..."
    CHAR_INITIAL_XP = "Initiale Generierungspunkte"
    CHAR_STARTING_CAPITAL = "Startkapital"
    CHAR_LOADED = "geöffnet"
    CHAR_SAVED = "gespeichert"
    CHAR_SWITCHED_EDIT_MODE = "Bearbeitungsmodus gewechselt"
    CHAR_ATTRIBUTE_CHANGED = "verändert"
    CHAR_SKILL_ADDED = "aktiviert"
    CHAR_SKILL_REMOVED = "entfernt"
    CHAR_SKILL_CHANGED = "geändert"
    CHAR_TRAIT_ADDED = "hinzugefügt"
    CHAR_TRAIT_REMOVED = "entfernt"
    CHAR_DATA_CREATED = "erstellt"
    CHAR_DATA_UPDATED = "aktualisiert"
    CHAR_ITEM_ADDED = "erworben"
    CHAR_ITEM_DESTROY = "zerstört"
    CHAR_ITEM_SELL = "verkauft"
    CHAR_ITEM_SPLIT = "abgeteilt"
    CHAR_ITEM_CONDENSED = "zusammengeführt"
    CHAR_ITEM_ROTATECHAMBER = "Kammer gewechselt"
    CHAR_ITEM_BAG = "bag"
    CHAR_ITEM_PACKED = "eingepackt"
    CHAR_ITEM_UNPACKED = "entnommen"
    CHAR_ITEM_EQUIP = "angelegt"
    CHAR_ITEM_UNEQUIP = "abgelegt"
    CHAR_ITEM_UPDATE = "geändert"
    CHAR_ITEM_DESCRIPTION = "Beschreibung geändert"
    CHAR_ITEM_RENAMED = "umbenannt"
    CHAR_CONTACT_NEW = "erstellt"

    # LOG DISPLAY
    LOG_HEADER = " ΔXP     Zeitpunkt:                  Ereignis:"
    LOG_XP_CHANGED = "Verfügbare XP: {total} ({delta})"
    LOG_ITEM_ADDED = "%s zum Inventar hinzugefügt - Gesamtmenge: %d"
    LOG_ITEM_RENAMED = "%s in %s umbenannt."
    LOG_ITEM_PACKED = "{name} in {container} eingelegt."
    LOG_ITEM_UNPACKED = "{name} aus {container} entnommen."
    LOG_CONTACT_CHANGED = "ID: {id} - {name} {diff}"
    LOG_CONTACT_RENAMED = "umbenannt in: "
    LOG_CONTACT_COMPETENCY = "Kompetenz: "
    LOG_CONTACT_LOYALITY = "Loyalität: "
    LOG_CONTACT_FREQUENCY = "Kontakthäufigkeit: "
    LOG_CONTACT_LOCATION = "Aufenthaltsort: "
    LOG_CONTACT_DESC = "Beschreibung"
    LOG_CONTACT_DESC_CHANGED = " geändert"
    LOG_CONTACT_DESC_DELETED = " gelöscht"

    # Tooltip messages
    TT_ADD_TRAITS = "Hier klicken zum hinzufügen\nneuer Eigenschaften."


    phy = "Physisch"
    men = "Mental"
    soz = "Sozial"
    nk = "Nahkampf"
    fk = "Fernkampf"
    lp = "Lebenspunkte"
    ep = "Energiepunkte"
    mp = "Moralpunkte"


# THIS CLASS DEFINES VALUES CONCERNING PDF EXPORTS
class Page:
    """ 
    The Page class defines core variables for the PDF Export. 
    """
    # Size parameters:
    #  WARNING: These parameters are used to evaluate data
    #  from XML files. Changing these will break import of
    #  templates created on other machines and will make it
    #  impossible to import your templates on other computers!
    SINGLE = 'single'
    DOUBLE = 'double'
    TRIPLE = 'triple'
    FULL = 'full'
    WIDE = 'wide'
    QUART = 'quart'
    BIG = 'big'
    HALF = 'half'
    ATTRIB_IMAGE = 'attrimg'

    # defining module sizes in points ... 
    #  These were created for A4 pages!
    SINGLE_WIDTH = 193
    DOUBLE_WIDTH = 400
    SINGLE_HEIGHT = 131
    DOUBLE_HEIGHT = 276
    TRIPLE_HEIGHT = 421
    FULL_HEIGHT = 566
        
    BAR_WIDTH = 20
    OUTER_RADIUS = 4
    INNER_RADIUS = 2
    Y_PADDING = 2
    SPACER = 14
    MINLINE_HEIGHT = 14
    INFO_LINE = 9
    STROKE = 1

    # Module names:
    #  WARNING: These parameters are used to evaluate data
    #  from XML files. Changing these will break import of
    #  templates created on other machines and will make it
    #  impossible to import your templates on other computers!
    MOD_ATTRIBUTES = "attributes"
    MOD_TRAITS = "traits"
    MOD_SKILLS = "skills"
    MOD_EQUIPMENT = "equipment"
    MOD_WEAPONS = "weapons"
    MOD_CONTACTS = "contacts"
    MOD_EWT = "ewt"
    MOD_NOTES = "notes"
    MOD_IMAGE = "image"


# this class handles the names of item types that are imported via xml
class ItemTypes:
    #  clothing and armor
    CLOTHING = "Kleidung"
    HARNESS = "Harnisch"
    ARMOR = "Rüstung"

    #  melee weapons 
    NATURAL = "Natürlich"
    CLUBS = "Hiebwaffen"
    BLADES = "Klingenwaffen"
    STAFFS = "Stabwaffen"
    OTHER_MELEE = "Andere Nahkampfwaffen"

    #  guns 
    REVOLVERS = "Revolver"
    PISTOLS = "Pistolen"
    RIFLES = "Gewehre"
    SHOT_GUNS = "Flinten"
    RIFLES_SA = "Gewehre-SA"
    SHOT_GUNS_SA = "Flinten-SA"
    AUTOMATIC_RIFLES = "Sturmgewehre"
    AUTOMATIC_PISTOLS = "Maschinenpistolen"
    MASCHINE_GUNS = "Maschinengewehre"
    BLASTER = "Blaster"

    #  various
    TOOLS = "Werkzeug"
    CLIP = "Clip"
    AMMO = "Munition"
    MONEY = "Geld"

    #  containers
    BAG = "Tasche"
    BOX = "Kiste"
    CONTAINER = "Container"

    #  other stuff
    SERVICES = "Dienstleistungen"
    MONEY = "Geld"
    GENERIC = "Diverses"

    OPTION_CALIBER = "Kaliber"
    OPTION_COLOR = "Farbe"


# this class handles character XML data names
class Character:
    # attributes
    PHY = "phy"
    MEN = "men"
    SOZ = "soz"

    NK = "nk"
    FK = "fk"

    LP = "lp"

    # data
    NAME = "name"
    SPECIES = "species"
    ORIGIN = "origin"
    CONCEPT = "concept"
    PLAYER = "player"
    HEIGHT = "height"
    WEIGHT = "weight"
    AGE = "age"
    GENDER = "gender"
    HAIR = "hair"
    EYES = "eyes"
    SKIN = "skin"
    SKIN_TYPE = "skintype"


class Colors:
    BLACK = "#000000"
    DARK_RED = "#dd0000"
    DARK_GREEN = "#00aa00"
    LIGHT_YELLOW = "#ffffcc"


class Style:
    FONT = "Arial"
    SIZE = "10"