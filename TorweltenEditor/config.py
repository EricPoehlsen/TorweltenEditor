# coding=utf-8
"""
This file provides several classes containing constants. Some of these
constants may be retrieved from XML files ...
"""


# defining the EWT
#       -7  -6  -5  -4  -3  -2  -1   0   1   2   3   4   5   6   7 
EWT = [[2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0,2.0,1.0,1.0,1.0,1.0,0.5],  # 1
       [2.0,2.0,2.0,2.0,2.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.0,0.0],  # 2
       [2.0,2.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.0,0.0,0.0],  # 3
       [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.0,0.0,0.0,0.0],  # 4
       [1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0],  # 5
       [1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0],  # 6
       [1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0],  # 7
       [1.0,1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],  # 8
       [1.0,1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],  # 9
       [1.0,0.5,0.5,0.5,0.5,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]]  # 0


# THIS CLASS CONTAINS MESSAGES TO BE DISPLAYED ON THE UI OR PDF EXPORTS
class Messages:
    """ Messages provides a variety of strings for the UI and PDF Export """

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
    MONEYFORMAT = "%.2f R"
    MONEYSPLIT = ","
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
    TOOLBAR_CHAR_DATA = "Charakterdaten"
    TOOLBAR_CHAR_EQUIP = "Inventar"
    TOOLBAR_CHAR_CONTACTS = "Kontakte"
    TOOLBAR_CHAR_IMAGE = "Charakterbild"
    TOOLBAR_CHAR_NOTES = "Notizen"
    TOOLBAR_CHAR_LAYOUT = "PDF-Export"

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
    TS_SEARCH = "Suche"
    TS_TRAIT = "Eigenschaft"
    TS_DESCRIPTION = "Beschreibung ..."
    TS_ADD_TRAIT = "Ausgewählte Eigenschaft hinzufügen ..."
    TS_JUST_SCROLL = "Gruppe wählen ..."
    TS_POSITIVE = "pos."
    TS_NEGATIVE = "neg."

    TS_BODY = "Körperbau"
    TS_MIND = "Geistig"
    TS_SOCIAL = "Sozial"
    TS_PERCEPTION = "Wahrnehmung"
    TS_FINANCIAL = "Vermögen"
    TS_FIGHTING = "Kampf"
    TS_ILLNESS = "Erkrankung"
    TS_TEMPORAL = "Temporales"
    TS_SKILL = "Fertigkeiten"
    TS_BEHAVIOR = "Verhalten"
    TS_XS = "Extraspatiales"
    TS_PSI = "Psionik"

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
    ES_BUY_BUTTON = "Ausrüstung einkaufen"
    ES_EQUIPPED = "Mitgeführte Ausrüstung"
    ES_MELEE = "Nahkampfwaffen"
    ES_GUNS = "Fernkampfwaffen"
    ES_UNASSIGNED = "Nicht zugewiesen"
    ES_INITIAL_FUNDS = "Startkapital: {amount},00 Rand"
    ES_CLOTHING_ARMOR = "Kleidung und Rüstung"
    ES_BIOTECH = "Kybernetik"
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
    ES_TT_EQUIP = "Gegenstand anlegen."
    ES_TT_UNEQUIP = "Gegenstand ablegen."
    ES_TT_PACK = "Gegenstand in Tasche packen."
    ES_TT_UNPACK = "Gegenstand auspacken."
    ES_TT_ACTIVE_BAG = "Aktiver Behälter, gewählte Gegenstände\n"\
                       "werden hier eingelegt"
    ES_TT_INACTIVE_BAG = "Behälter ist derzeit inaktiv,\n"\
                         "anklicken zum aktivieren ..."

    # ####ITEM EDITOR and INVENTORY EDITOR # ####
    IE_DESTROY = "Zerstören"
    IE_KG = " kg"
    IE_G = " g"
    IE_WEIGHT = "Gewicht: "
    IE_PRICE_VALUE = "Wert: "
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
    IE_QUALITY_1 = "kaputt"
    IE_QUALITY_2 = "beschädigt"
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
    IE_BUY = "Kaufen"
    IE_PRICE = "Preis"
    IE_DAMAGE = "Schaden: {value}"
    IE_TYPE_CLOTHING = "Bekleidung oder Rüstung"
    IE_TYPE_MELEE = "Nahkampfwaffe"
    IE_TYPE_GUNS = "Fernkampfwaffe"
    IE_TYPE_CONTAINER = "Behälter"
    IE_TYPE_TOOLS = "Werkzeug"
    IE_TYPE_AMMO = "Munition"
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
    IE_IMPLANT = "Implantieren ..."
    IE_IMPLANT_ADDONS = "Einbauten: "
    IE_ATTACHED_TO = "angesetzt an: "
    IE_BUILT_INTO = "eingebaut in: "
    IE_CLOTHING_GROUP = "Kleidung und Taschen"  # group in items.xml
    IE_CLOTHING_EDITOR = "Bekleidungsbaukasten"
    IE_CE_RANDOM = "zufälliges Kleidungsstück"
    IE_CE_GENERATE = "generieren ..."
    IE_CE_SELECTION = "Optionen wählen"
    IE_CE_HEAD = "Kopf"
    IE_CE_NECK = "Hals"
    IE_CE_TORSO = "Oberkörper"
    IE_CE_UPPERARMS = "Oberarme"
    IE_CE_FOREARMS = "Unterarme"
    IE_CE_HANDS = "Hände"
    IE_CE_HIPS = "Hüfte"
    IE_CE_UPPERLEGS = "Oberschenkel"
    IE_CE_LOWERLEGS = "Unterschenkel"
    IE_CE_FEET = "Füße"
    IE_CE_CHOSEN = "ausgewählt"
    IE_CE_ARMOR1 = "robuste"
    IE_CE_ARMOR2 = "gepanzerte"
    IE_CE_CLOSURE = "Verschluss"
    IE_CE_COMPLEX = "Komplexer Schnitt"
    IE_CE_CANVAS = "Viel Stoff"
    IE_CE_TRIMMINGS = "Verzierungen"
    IE_CE_POCKETS = "Taschen"
    IE_CE_FABRIC = "Materialqualität"
    IE_CE_FABRIC_NAME = "Material"
    IE_CE_FABRIC_COLOR = "Farbe"
    IE_CE_TROUSERS = "Hosenbeine"
    IE_CE_SIMPLE = "einfach / schlicht"
    IE_CE_ELEGANT = "elegant / hochwertig"
    IE_CE_RARE = "exquisit / selten"
    IE_CE_SINGLE_LAYER = "leicht, einlagig"
    IE_CE_MULTI_LAYER = "gefüttert, mehrlagig"
    IE_CE_MULTI_HEAVY = "robust, schwer"

    # grammaticals ...
    IE_CE_LJOIN = "e"
    IE_CE_NJOIN = "n"
    M = "r"
    F = ""
    N = "s"
    G_ART = {
        "M": "Der",
        "F": "Die",
        "N": "Das",
    }
    N_ART = {
        "M": "Ein",
        "F": "Eine",
        "N": "Ein",
    }
    N_ART_ACC = "einen"

    # names
    IE_CE_UNKNOWN = "Kleidungsstück", N
    IE_CE_HOOD = "Kapuzen", F
    IE_CE_HAT = "Hut", M
    IE_CE_CAP = "Mütze", F
    IE_CE_MASK = "Maske", F
    IE_CE_TURBAN = "Turban", M
    IE_CE_GUGEL = "Gugel", F
    IE_CE_HELMET = "Helm", M
    IE_CE_HEAD_SCARF = "Kopftuch", N
    IE_CE_SCARF = "Halstuch", N
    IE_CE_COLLAR = "Kragen"
    IE_CE_TIE = "Krawatte", F
    IE_CE_MUFFLER = "Schal", M
    IE_CE_SHIRT = "Hemd", N
    IE_CE_UNDERSHIRT = "Unterhemd", N
    IE_CE_WEST = "Weste", F
    IE_CE_T_SHIRT = "T-Shirt", N
    IE_CE_POLOSHIRT = "Poloshirt", N
    IE_CE_SWEATER = "Pullover", M
    IE_CE_JACKET = "Jacke", F
    IE_CE_COAT = "Mantel", M
    IE_CE_CAPE = "Cape", N
    IE_CE_BODY = "Body", M
    IE_CE_VAMBRACE = "Paar Armschienen", N
    IE_CE_GLOVES = "Paar Handschuhe", N
    IE_CE_BRIEFS = "Unterhose", F
    IE_CE_PANTS = "Hose", F
    IE_CE_DUNGAREES = "Latzhose", F
    IE_CE_TIGHTS = "Strumpfhose", F
    IE_CE_JAMBART = "Paar Beinschienen", F
    IE_CE_OVERALL = "Overall", M
    IE_CE_SKIRT = "Rock", M
    IE_CE_DRESS = "Kleid", N
    IE_CE_SOCKS = "Paar Socken", N
    IE_CE_SHOES = "Paar Schuhe", N
    IE_CE_BOOTS = "Paar Stiefel", N
    IE_CE_NAMESPLIT = "Paar"

    # this is used for the name lookup ...
    IE_CLOTHING_NAMES = {
        "10000000001": IE_CE_CAP,
        "20000000001": IE_CE_HAT,
        "X000000000H": IE_CE_HAT,
        "F0000000001": IE_CE_TURBAN,
        "1000000000A": IE_CE_HELMET,
        "11000000001": IE_CE_MASK,
        "12000000001": IE_CE_GUGEL,
        "1F000000001": IE_CE_GUGEL,
        "XC00000000X": IE_CE_GUGEL,
        "FF000000001": IE_CE_HEAD_SCARF,
        "F1000000001": IE_CE_HEAD_SCARF,
        "XX00000000X": IE_CE_GUGEL,
        "01000000001": IE_CE_SCARF,
        "02000000001": IE_CE_SCARF,
        "0C00000000X": IE_CE_TIE,
        "0F00000000X": IE_CE_MUFFLER,
        "01100000001": IE_CE_SHIRT,
        "00100000001": IE_CE_UNDERSHIRT,
        "0XC0000000X": IE_CE_WEST,
        "00X0000000X": IE_CE_WEST,
        "0XC000C000X": IE_CE_WEST,
        "00C0000000X": IE_CE_WEST,
        "00C000C000X": IE_CE_WEST,
        "XXC0000000X": IE_CE_WEST,
        "XXC000C000X": IE_CE_WEST,
        "XXC000CXX0X": IE_CE_WEST,
        "0XX0000000X": IE_CE_WEST,
        "00C000CX00H": IE_CE_WEST,
        "00110000001": IE_CE_T_SHIRT,
        "1010000000X": IE_CE_T_SHIRT,
        "01110000001": IE_CE_POLOSHIRT,
        "02110000001": IE_CE_POLOSHIRT,
        "00XXX00000X": IE_CE_SWEATER,
        "0XXXX00000X": IE_CE_SWEATER,
        "XXXXX00000X": IE_CE_SWEATER,
        "00CX0000001": IE_CE_SHIRT,
        "00CXX000001": IE_CE_SHIRT,
        "0XCX0000001": IE_CE_SHIRT,
        "0XCXX000001": IE_CE_SHIRT,
        "00CXX00000X": IE_CE_JACKET,
        "0XCXX00000X": IE_CE_JACKET,
        "XXCXX00000X": IE_CE_JACKET,
        "00CXX0C000A": IE_CE_COAT,
        "00CXX0CXX0A": IE_CE_COAT,
        "0XCXX0C000A": IE_CE_COAT,
        "0XCXX0CXX0A": IE_CE_COAT,
        "XXCXX0C000A": IE_CE_COAT,
        "XXCXX0CXX0A": IE_CE_COAT,
        "0XCXX0CXX0X": IE_CE_COAT,
        "XXCXX0XXX0X": IE_CE_COAT,
        "XXCXX0CXX0X": IE_CE_COAT,
        "0XCXX0XXX0X": IE_CE_COAT,
        "0XCXX0CXX0H": IE_CE_COAT,
        "00CXX0XXX0X": IE_CE_COAT,
        "00C000C0001": IE_CE_DRESS,
        "00C000CXX01": IE_CE_DRESS,
        "00C000C000H": IE_CE_DRESS,
        "00C000CXX0H": IE_CE_DRESS,
        "00CXX0CXX01": IE_CE_DRESS,
        "0XX000X000X": IE_CE_DRESS,
        "0XCXX0CXX01": IE_CE_DRESS,
        "00CXX0XXX01": IE_CE_DRESS,
        "00CX00C000H": IE_CE_DRESS,
        "00CX00CX00H": IE_CE_DRESS,
        "00CX00CXX0H": IE_CE_DRESS,
        "XXCXX0XXX01": IE_CE_DRESS,
        "XXCXX0CXX01": IE_CE_DRESS,
        "XXXXX0CXX01": IE_CE_DRESS,
        "XXXXX0XXX0X": IE_CE_DRESS,
        "00XXX0CXX0X": IE_CE_DRESS,
        "00XXX0XXX0X": IE_CE_DRESS,
        "0XXXX0CXX0X": IE_CE_DRESS,
        "XXXXX0XXX01": IE_CE_DRESS,
        "XXXXX0CXX0X": IE_CE_DRESS,
        "0XXXX0XXX0X": IE_CE_DRESS,
        "02F000F0001": IE_CE_CAPE,
        "02F000FF001": IE_CE_CAPE,
        "02F000FFF01": IE_CE_CAPE,
        "22F000F0001": IE_CE_CAPE,
        "22F000FF001": IE_CE_CAPE,
        "22F000FFF01": IE_CE_CAPE,
        "XXX000XXX0X": IE_CE_CAPE,
        "XXCXX0TXX0X": IE_CE_OVERALL,
        "0XCXX0TXX0X": IE_CE_OVERALL,
        "00CXX0TXX0X": IE_CE_OVERALL,
        "XXXXX0TXX0X": IE_CE_BODY,
        "0XXXX0TXX0X": IE_CE_BODY,
        "00XXX0TXX0X": IE_CE_BODY,
        "000XXX0000X": IE_CE_GLOVES,
        "0000XX0000X": IE_CE_GLOVES,
        "00000X0000X": IE_CE_GLOVES,
        "0000X00000X": IE_CE_VAMBRACE,
        "000000CXX0X": IE_CE_SKIRT,
        "000000XXX0X": IE_CE_SKIRT,
        "00C000T000X": IE_CE_DUNGAREES,
        "00C000TX00X": IE_CE_DUNGAREES,
        "00C000TXX0X": IE_CE_DUNGAREES,
        "000000TXX0X": IE_CE_PANTS,
        "00000000X0X": IE_CE_JAMBART,
        "000000000X1": IE_CE_SOCKS,
        "00000000XX1": IE_CE_SOCKS,
        "0000000XXX1": IE_CE_SOCKS,
        "000000TXXX1": IE_CE_TIGHTS,
        "000000000XX": IE_CE_SHOES,
        "00000000XXX": IE_CE_BOOTS,
        "0000000XXXX": IE_CE_BOOTS,
    }

    # size options
    IE_CE_VERY = "sehr"
    IE_CE_WIDE = "weit"
    IE_CE_TIGHT = "eng"
    IE_CE_MINI = "mini"
    IE_CE_LONG = "lang"
    IE_CE_SHORT = "kurz"
    IE_CE_HIGH = "hohe"
    IE_CE_RICH = "reich"
    IE_CE_ARMLY = "ärmlige"

    # addons
    IE_CE_ADD_DESC1 = "{art}{cut}{name}{has}{arms}{style}"
    IE_CE_TRIMMED = "verziert"
    IE_CE_PRIMITIVE = "einfachen"
    IE_CE_INTRICATE = "aufwändigen"
    IE_CE_EMBROIDERED = "bestickt"
    IE_CE_SLEEVES = "Ärmel"
    IE_CE_TRUMPET_SLEEVES = "Trompetenärmel"
    IE_CE_PUFF_SLEEVES = "Puffärmel"
    IE_CE_CONFORMING = "figurbetont"
    IE_CE_SLIM = "gut sitzend"
    IE_CE_COMFY = "bequem"
    IE_CE_CUTLY = "geschnittene"
    IE_CE_COAT_LEG_0 = "enge"
    IE_CE_COAT_LEG_1 = "weite"
    IE_CE_COAT_LEG_2 = "ausladende"
    IE_CE_DRESS_LEG_0 = "beinumschmeichelnde"
    IE_CE_DRESS_LEG_1 = "lockere"
    IE_CE_DRESS_LEG_2 = "weitsäumige"
    IE_CE_PANTS_LEG_0 = "engbeinige"
    IE_CE_PANTS_LEG_1 = "lockere"
    IE_CE_PANTS_LEG_2 = "legere"
    IE_CE_CUT = "Schnitt"
    IE_CE_HAS = [
        "besitzt",
        "hat",
        "verfügt über"
    ]

    YELLOW = "gelb"
    ORANGE = "orange"
    BLUE = "blau"
    TURQUOISE = "türkis"
    BROWN = "braun"
    GREEN = "grün"
    PINK = "pink"
    ROSE = "rosa"
    VIOLET = "violett"
    MAGENTA = "magenta"
    RED = "rot"
    WHITE = "weiß"
    GREY = "grau"
    BLACK = "schwarz"

    LIGHT = "hell"
    DARK = "dunkel"
    SHIMMERING = "schimmernd"
    NEON = "neon"
    COLOR = "farben"
    COLOR_JOIN = "-"
    NOT_LIGHT = [BLACK, WHITE]
    NOT_DARK = [BLACK, WHITE]
    NOT_NEON = [TURQUOISE, BROWN, ROSE, VIOLET, MAGENTA, WHITE, GREY, BLACK]

    ALL_COLORS = [
        YELLOW,
        ORANGE,
        BLUE,
        TURQUOISE,
        BROWN,
        GREEN,
        PINK,
        ROSE,
        VIOLET,
        MAGENTA,
        RED,
        WHITE,
        GREY,
        BLACK,
    ]
    COLOR_COMBO = {
        WHITE: ALL_COLORS,
        BLACK: ALL_COLORS,
        GREY: ALL_COLORS,
        YELLOW: [ORANGE, BLUE, BROWN, GREEN, RED, WHITE, GREY, BLACK],
        ORANGE: [YELLOW, BROWN, GREEN, RED, WHITE, GREY, BLACK],
        RED: [YELLOW, ORANGE, BROWN, WHITE, GREY, BLACK],
        BROWN: [YELLOW, ORANGE, GREEN, ROSE, VIOLET, RED, WHITE, GREY, BLACK],
        GREEN: [YELLOW, BLUE, WHITE, GREY, BLACK],
        TURQUOISE: [YELLOW, WHITE, GREY, BLACK],
        BLUE: [YELLOW, ORANGE, BROWN, GREEN, RED, WHITE, GREY, BLACK],
        PINK: [YELLOW, WHITE, GREY, BLACK],
        ROSE: [YELLOW, BROWN, WHITE, GREY, BLACK],
        VIOLET: [YELLOW, WHITE, GREY, BLACK],
        MAGENTA: [YELLOW, WHITE, GREY, BLACK]
    }

    CHECKERED = "kariert"
    STRIPED = "gestreift"
    SPOTTED = "gepunktet"
    CAMOUFLAGE = "camouflage-gemustert"
    TIGERED = "getigert"
    PATTERNED = "gemustert"
    PLAIN = "einfarbig"
    PATTERNS = [
        CHECKERED,
        STRIPED,
        SPOTTED,
        TIGERED,
        CAMOUFLAGE,
        PATTERNED,
    ]

    IE_CE_SLEEVE_DICT = {
        "00": "",
        "10": IE_CE_SHORT + IE_CE_LJOIN + " " + IE_CE_SLEEVES,
        "20": IE_CE_SHORT + IE_CE_LJOIN + " " + IE_CE_PUFF_SLEEVES,
        "11": IE_CE_LONG + IE_CE_LJOIN + " " + IE_CE_SLEEVES,
        "21": IE_CE_LONG + IE_CE_LJOIN + " " + IE_CE_PUFF_SLEEVES,
        "12": IE_CE_TRUMPET_SLEEVES,
        "22": " ".join([IE_CE_VERY, IE_CE_WIDE, IE_CE_CUTLY, IE_CE_SLEEVES])
    }

    # closures
    IE_CE_NO_CLOSURE = "nicht gewählt"
    IE_CE_CLOSURE_DESC = "Als Verschluss dien{gendered} {variant} {closure}."
    IE_CE_ZIPPER = "Reißverschluss"
    IE_CE_ZIPS = [
        "versteckter",
        "gerader",
        "geschwungener",
        "kurzer",
        "langer",
    ]
    IE_CE_BUTTONS = "Knopfleiste"
    IE_CE_BUTS = [
        "versteckte",
        "gerade",
        "geschwungene",
        "einfache",
        "doppelte",
    ]
    IE_CE_VELCRO = "Klettverschluss"
    IE_CE_VELCS = [
        "versteckter",
        "einfacher",
        "doppelter",
        "gesicherter"
    ]
    IE_CE_LACING = "Schnürung"
    IE_CE_LACES = [
        "versteckte",
        "einfache",
        "aufwändige",
        "elegante"
    ]
    IE_CE_BUCKLES = "Schnallen"
    IE_CE_BUCKS = [
        "versteckte",
        "gesicherte"
    ]
    IE_CE_CLOSURE_GENDERS = {
        IE_CE_BUTTONS: "t eine",
        IE_CE_ZIPPER: "t ein",
        IE_CE_VELCRO: "t ein",
        IE_CE_LACING: "t eine",
        IE_CE_BUCKLES: "en",
    }

    # quality descriptions:
    IE_CE_USED = "Das {part} ist {state} und von ursprünglich {quality}."
    IE_CE_NEW = "Das {part} ist von {quality}."
    IE_CE_PART = ["Stück", "Teil"]
    IE_CE_NEW_QUAL = {
        3: "mieserabler",
        4: "sehr schlechter",
        5: "schlechter ",
        6: "üblicher",
        7: "ordentlicher",
        8: "sehr guter",
        9: "herausragender",
    }
    IE_CE_USED_QUAL = {
        3: "geflickt",
        4: "abgetragen",
        5: "gut erhalten",
        6: "fast neuwertig",
        7: "wie neu",
        8: "neuwertig",
    }

    # fabrics (used for auto-generator)
    # name, minlayers, maxlayers, pricerange
    IE_CE_COTTON = "Baumwolle", 0, 2, 0
    IE_CE_WOOL = "Wolle", 1, 2, 1
    IE_CE_LEATHER = "Leder", 1, 2, 2
    IE_CE_SYNTH_LEATHER = "Synthleder", 1, 2, 1
    IE_CE_NYLON = "Nylon", 0, 1, 0
    IE_CE_FIBRES = "Kunstfaser", 0, 1, 1
    IE_CE_PELT = "Pelz", 1, 2, 2
    IE_CE_SYNTH_PELT = "Kunstfell", 1, 2, 0
    IE_CE_LATEX = "Latex", 0, 0, 1
    IE_CE_POLYESTER = "Polyester", 0, 1, 1
    IE_CE_SILK = "Seide", 0, 1, 2
    IE_CE_SYNTH_SILK = "Synthseide", 0, 1, 1
    IE_CE_SPANDEX = "Spandex", 0, 0, 0
    IE_CE_FLANELL = "Flanell", 0, 1, 0
    IE_CE_SATIN = "Satin", 0, 1, 0
    IE_CE_VELVET = "Samt", 0, 2, 2
    IE_CE_SYNTH_VELVET = "Pannesamt", 0, 1, 0
    IE_CE_LINEN = "Leinen", 0, 2, 1
    IE_CE_FLEECE = "Fleece", 0, 1, 0
    IE_CE_JAQUARD = "Jaquard", 1, 2, 2
    IE_CE_FROTTEE = "Frottee", 0, 1, 0
    IE_CE_JEANS = "Jeans", 0, 1, 1
    IE_CE_CORD = "Cord", 0, 1, 1
    IE_CE_LODEN = "Loden", 1, 2, 2
    IE_CE_TWEED = "Tweed", 1, 2, 2
    IE_CE_RUBBER = "Gummi", 0, 2, 0
    IE_CE_ADDN = ["eide"]
    IE_CE_DELE = ["olle"]

    IE_CE_FABRICS = [
        IE_CE_COTTON,
        IE_CE_WOOL,
        IE_CE_LEATHER,
        IE_CE_SYNTH_LEATHER,
        IE_CE_NYLON,
        IE_CE_FIBRES,
        IE_CE_PELT,
        IE_CE_POLYESTER,
        IE_CE_SILK,
        IE_CE_SYNTH_SILK,
        IE_CE_SPANDEX,
        IE_CE_FLANELL,
        IE_CE_SATIN,
        IE_CE_VELVET,
        IE_CE_SYNTH_VELVET,
        IE_CE_LINEN,
        IE_CE_FLEECE,
        IE_CE_JAQUARD,
        IE_CE_FROTTEE,
        IE_CE_LODEN,
        IE_CE_TWEED,
        IE_CE_LATEX,
        IE_CE_SYNTH_PELT,
        IE_CE_JEANS,
        IE_CE_CORD,
        IE_CE_RUBBER,
    ]

    IE_CE_NOT_GLOVES = [
        IE_CE_LINEN,
        IE_CE_FLANELL,
        IE_CE_JAQUARD,
        IE_CE_FROTTEE,
        IE_CE_LODEN,
        IE_CE_TWEED,
        IE_CE_JEANS,
        IE_CE_CORD,
    ]

    IE_CE_NOT_SOCKS = [
        IE_CE_LEATHER,
        IE_CE_SYNTH_LEATHER,
        IE_CE_PELT,
        IE_CE_FLANELL,
        IE_CE_SATIN,
        IE_CE_VELVET,
        IE_CE_SYNTH_VELVET,
        IE_CE_LINEN,
        IE_CE_JAQUARD,
        IE_CE_FROTTEE,
    ]

    IE_CE_NOT_SHOES = [
        IE_CE_LEATHER,
        IE_CE_SYNTH_LEATHER,
        IE_CE_PELT,
        IE_CE_LATEX,
        IE_CE_SYNTH_PELT,
    ]

    # pockets
    IE_CE_POCKETS_0 = ""  # I left it blank intentionally (but can be used)
    IE_CE_POCKETS_1 = "mit einer Tasche"
    IE_CE_POCKETS_2 = "mit zwei Taschen"
    IE_CE_POCKETS_3 = "mit einigen Taschen"
    IE_CE_POCKETS_4 = "mit vielen Taschen"

    IE_TT_LIST = "Liste der Ausrüstungsgegenstände"
    IE_TT_CE = "Bekleidungsbaukasten"
    IE_TT_CUSTOM = "Gegenstand erstellen"

    IE_TT_SELECTED = "Bedeckt das Kleidungsstück\ndieses Körperteil?"
    IE_TT_ARMOR1 = "robuste Ausführung 0/+1 Panzerung"
    IE_TT_ARMOR2 = "gepanzerte Ausführung - 0/+2"
    IE_TT_CLOSURE = "An diesem Element befinden sich Verschlüsse"
    IE_TT_COMPLEX = "Dieser Teil des Kleidungsstücks\n"\
                    "besitzt einen aufwändigen Schnitt"
    IE_TT_FABRIC = "Sehr viel Stoff (z.B Trompetenärmel oder Rock)"
    IE_TT_TRIMMINGS = "Dieses Element ist bestickt oder anders verziert."
    IE_TT_POCKETS = "An diesem Teil befinden sich Taschen."
    IE_TT_CLOSURE_TYPE = "Art des Verschlusses. Nur\n"\
                         "wählbar, wenn auch ein\n"\
                         "Verschluss ausgewählt ist.\n"\
                         "[nur für die Auto-Beschreibung]"
    IE_TT_MATERIAL = "Material festlegen.\nWird als Option übernommen"
    IE_TT_COLOR = "Farbe festlegen.\nWird als Option übernommen."
    IE_TT_PANTS = "Das Kleidungsstück hat Hosenbeine\n"\
                  "Nur wählbar wenn 'Hüfte' aktiv.\n"\
                  "[für die Auto-Beschreibung relevant]"
    IE_TT_CE_BUY = "Kleidungsstück kaufen\nDer Preis steht auch hier."

    IE_TT_NAME = "Alles braucht einen Namen"
    IE_TT_QUANTITY = "Anzahl\n(nur positive Zahlen)"
    IE_TT_WEIGHT = "Gewicht\npro Stück\nin Gramm"
    IE_TT_QUALITY = "Qualitätsstufe:\n1 - 9"
    IE_TT_AVAIL = "Verfügbarkeit:\n-6 - +6"
    IE_TT_PRICE = "Gesamtpreis\n(wird durch Anzahl geteilt!)"
    IE_TT_DAMAGE = "Schaden im Format:\n±S/±D"
    IE_TT_CALIBER = "Waffen, Magazine und Munition\n"\
                    "passen nur zusammen, wenn dieser\n"\
                    "Wert übereinstimmt."
    IE_TT_CONTAINER = "Anzeigename der Taschen\n(z.B. Hosentaschen)"

    IE_TT_EQUIP = "Gegenstand anlegen."
    IE_TT_UNEQUIP = "Gegenstand ablegen."
    IE_TT_SPLIT = "Stapel teilen"
    IE_TT_SPLIT_AMOUNT = "Welche Menge abteilen"
    IE_TT_CONDENSE = "Gleiche Gegenstände zusammenführen"
    IE_TT_DESTROY = "zerstören / verbrauchen"
    IE_TT_SELL = "Gegenstand verkaufen"
    IE_TT_REPAIR = "Gegenstand reparieren / verbessern"
    IE_TT_DAMAGE_ITEM = "Gegenstand beschädigen"


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
    SL_EMPTY = "[ L E E R ]"
    SL_EXPORT = "PDF Exportieren"
    SL_TT_NEW = "Neues Template erstellen ..."
    SL_TT_LOAD = "Template laden ..."
    SL_TT_SAVE = "Template speichern ..."
    SL_TT_LAST = "zurückblättern"
    SL_TT_NEXT = "weiterblättern"
    SL_TT_NEW_PAGE = "Seite einfügen"
    SL_TT_MOVE_UP = "Seite eins hoch schieben"
    SL_TT_MOVE_DOWN = "Seite eins runter schieben"
    SL_TT_DEL_PAGE = "Seite löschen"

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
    ME_SHOW_WEIGHT = "Gewicht"
    ME_SHOW_VALUE = "Wert"
    ME_CONTENTS = "Inhalt von:"
    ME_CONDENSED = "(zusammengefasst)"
    ME_EQUIPPED = "angelegte"
    ME_JUST_EQUIPPED = "(nur angelegte)"
    ME_ONLY_BAG = "Nur den Inhalt der nachfolgend\n gewählten Tasche zeigen:"
    ME_NOTES = "Die folgende Notiz verwenden ..."
    ME_NOT_SELECTED = "nichts gewählt"
    ME_NOTES_TITLE = "Erstelle ein leeres Feld mit folgendem Titel:"

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
    PDF_EQUIPMENT_ALL = "Alle"
    PDF_EQUIPMENT_TOOLS = "Werkzeug"
    PDF_EQUIPMENT_BIOTECH = "Biotech"
    PDF_EQUIPMENT_MONEY = "GELD & WERTSACHEN"
    PDF_EQUIPMENT_CLOTHING = "Kleidung und Rüstung"
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
    PDF_VALUE = "Wert"
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

    # SettingScreen
    SET_CORE_SETTINGS = "Programmoptionen"
    SET_INITIAL_XP = "Erfahrungspunkte für neue Charaktere"
    SET_INIT_XP_INVALID = "UNGÜLTIG"
    SET_CHAR_SETTINGS = "Charakteroptionen"
    SET_EDIT_MODE = "Bearbeitungsmodus wählen"
    SET_EDIT_GENERATION = "Charaktergenerierung"
    SET_EDIT_EDIT = "Bearbeitungsmodus"
    SET_EDIT_VIEW = "Ansichtsmodus"
    SET_EDIT_SIM = "Simulation"
    SET_EDIT_SWITCH = "Modus wechseln"
    SET_EXPANSIONS = "Erweiterungen auswählen: "

    # these strings are used in the character xml 
    CHAR_CREATED = "created"
    CHAR_INITIAL_XP = "init_xp"
    CHAR_STARTING_CAPITAL = "init_money"
    CHAR_LOADED = "loaded"
    CHAR_SAVED = "saved"
    CHAR_SWITCHED_EDIT_MODE = "editmode"
    CHAR_UPDATED = "updated"
    CHAR_ADDED = "added"
    CHAR_REMOVED = "removed"
    CHAR_ITEM_DESTROY = "destroyed"
    CHAR_ITEM_SELL = "sold"
    CHAR_ITEM_SPLIT = "split"
    CHAR_ITEM_CONDENSED = "joined"
    CHAR_ITEM_ROTATECHAMBER = "rotate_chamber"
    CHAR_ITEM_BAG = "bag"
    CHAR_ITEM_PACKED = "packed"
    CHAR_ITEM_UNPACKED = "unpacked"
    CHAR_ITEM_EQUIP = "equipped"
    CHAR_ITEM_UNEQUIP = "unequipped"
    CHAR_ITEM_DESCRIPTION = "description"
    CHAR_ITEM_RENAMED = "renamed"
    CHAR_ITEM_REPAIRED = "repaired"
    CHAR_ITEM_DAMAGED = "damaged"

    # LOG DISPLAY
    LOG_HEADER = " ΔXP     Zeitpunkt:                  Ereignis:"
    LOG_CHAR_CREATED = "Der Charakter wurde erstellt."
    LOG_CHAR_LOADED = "Charakterdatei geladen."
    LOG_CHAR_SAVED = "Charakterdatei gespeichert."
    LOG_XP_CHANGED = "Verfügbare XP: {total} ({delta})"
    LOG_ATTRIBUTE_CHANGED = "{name} Attribut geändert, neuer Wert: {value}"
    LOG_INITIAL_XP = "Erfahrungspunkte zur Charaktererschaffung: "
    LOG_DATA_ADDED = "{name} wurde neu gesetzt: {value}"
    LOG_DATA_UPDATED = "{name} wurde von {old} in {value} geändert."
    LOG_DATA_REMOVED = "Der Eintrag {name}: {old} wurde gelöscht."
    LOG_EDIT_GENERATION = "Charakter wurde in den Generierungsmodus gesetzt."
    LOG_EDIT_EDIT = "Charakter wurde in den Bearbeitungsmodus gesetzt."
    LOG_EDIT_VIEW = "Charakter wurde in den Ansichtsmodus versetzt."
    LOG_EDIT_SIM = "Charakter wurde in den Simulationsmodus gesetzt."
    LOG_SKILL_ADDED = "Fertigkeit {name} aktiviert."
    LOG_SKILL_UPDATED = "Fertigkeit {name} geändert. Neuer Wert ist {value}"
    LOG_SKILL_REMOVED = "Fertigkeit {name} entfernt."
    LOG_ITEM_ADDED = "{new} x {name} zum Inventar hinzugefügt"\
                     " insgesamt: {total}"
    LOG_ITEM_SPLIT = "{quantity}x {name} abgeteilt."
    LOG_ITEM_JOIN = "{name} zusammengeführt - Gesamtstapel: {quantity}"
    LOG_ITEM_SELL = "{quantity}x {name} verkauft."
    LOG_ITEM_DESTROY = "{quantity}x {name} zerstört."
    LOG_ITEM_RENAMED = "%s in %s umbenannt."
    LOG_ITEM_PACKED = "{name} in {container} eingelegt."
    LOG_ITEM_UNPACKED = "{name} aus {container} entnommen."
    LOG_ITEM_EQUIPPED = "{name} angelegt."
    LOG_ITEM_UNKNOWN = "[UNBEKANNT]"
    LOG_ITEM_DAMAGED = "{name} beschädigt, neue Qualität: {value}"
    LOG_ITEM_REPAIRED = "{name} repariert, neue Qualität: {value}"
    LOG_ACCOUNT_CAP_INC = "Startkapital um {amount} gesteigert."
    LOG_ACCOUNT_CAP_DEC = "Startkapital um {amount} reduziert."
    LOG_ACCOUNT_PAY_ITEM = "Ausrüstung bezahlt"
    LOG_CONTACT_CHANGED = "ID: {id} - {name} {diff}"
    LOG_CONTACT_RENAMED = "umbenannt in: "
    LOG_CONTACT_COMPETENCY = "Kompetenz: "
    LOG_CONTACT_LOYALITY = "Loyalität: "
    LOG_CONTACT_FREQUENCY = "Kontakthäufigkeit: "
    LOG_CONTACT_LOCATION = "Aufenthaltsort: "
    LOG_CONTACT_DESC = "Beschreibung"
    LOG_CONTACT_DESC_CHANGED = " geändert"
    LOG_CONTACT_DESC_DELETED = " gelöscht"
    LOG_CONTACT_UNKNOWN = "Ereignis zu gelöschtem Kontakt mit ID: "
    LOG_INTEGRITY = "Datenintegrität"
    LOG_OKAY = "Die gespeicherte Datei scheint in Ordnung zu sein."
    LOG_WARN = "Die gespeicherte Datei wurde extern bearbeitet!"
    LOG_UNSAVED = "Der Charakter wurde bisher nicht gespeichert"
    LOG_CORRUPT_FILE = "Externe Bearbeitung festgestellt ..."

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


class Values:
    """ Values that are needed somewhere ..."""

    # InventoryEditor and ItemEditor
    IE_BASE_PRICE1 = 5
    IE_BASE_PRICE2 = 2.5
    IE_PRICE_ARMOR = 10  # factor for each armor level
    IE_AREA_SMALL = 25
    IE_AREA_MEDIUM = 50
    IE_AREA_LARGE = 100


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


class ItemTypes:
    """ handling item import from xml files 
    
    Note:
        This handles how data from xml is parsed, changing it might
        break import of data files!
    """

    #  clothing and armor
    CLOTHING = "clothing"
    HARNESS = "harness"
    ARMOR = "armor"

    #  melee weapons 
    NATURAL = "natural"
    CLUBS = "club"
    BLADES = "blade"
    STAFFS = "staff"
    OTHER_MELEE = "other_melee"

    #  guns 
    REVOLVERS = "revolver"
    PISTOLS = "pistol"
    RIFLES = "rifle"
    SHOT_GUNS = "shotgun"
    RIFLES_SA = "rifle_sa"
    SHOT_GUNS_SA = "shotgun_sa"
    AUTOMATIC_WEAPON = "automatic_weapon"
    BLASTER = "blaster"

    #  various
    TOOLS = "tool"
    CLIP = "clip"
    AMMO = "ammo"
    MONEY = "money"
    GENERIC = "generic"

    #  containers
    BAG = "bag"
    BOX = "box"
    CONTAINER = "container"

    #  other stuff
    SERVICES = "service"
    FOOD = "food"
    DRUG = "drug"

    #biotech
    IMPLANT = "implant"
    PROSTHESIS = "prosthesis"
    IMPLANT_PART = "implant_part"

    OPTION_CALIBER = "caliber"
    OPTION_COLOR = "Farbe"


class TraitGroups:

    BODY = "body"
    MIND = "mind"
    SOCIAL = "social"
    PERCEPTION = "perception"
    FINANCIAL = "financial"
    FIGHTING = "fighting"
    ILLNESS = "illness"
    TEMPORAL = "temporal"
    SKILL = "skill"
    BEHAVIOR = "behavior"
    PSI = "psi"
    XS = "xs"


"""
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
"""


class Colors:
    BLACK = "#000000"
    DARK_RED = "#dd0000"
    DARK_GREEN = "#00aa00"
    LIGHT_YELLOW = "#ffffcc"


class Style:
    ATTR_FONT = "Arial 14 bold"

    ATTR_LF_FONT = "Arial 12 bold"
    TITLE_LF_FONT = "Arial 10 bold"
    BAG_LF_FONT = "Arial 9 bold"
