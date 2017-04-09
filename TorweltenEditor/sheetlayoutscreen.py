import xml.etree.ElementTree as et
import tkinter.filedialog as tkfd
from moduleeditor import ModuleEditor
from PIL import ImageTk, Image, PngImagePlugin
import tk_ as tk
import config
from tooltip import ToolTip
page = config.Page()
msg = config.Messages()


class LayoutScreen(tk.Frame):
    sizes = {
        page.SINGLE: (1, 1),
        page.DOUBLE: (2, 1),
        page.TRIPLE: (3, 1),
        page.FULL: (4, 1),
        page.WIDE: (1, 2),
        page.QUART: (2, 2),
        page.BIG: (3, 2),
        page.HALF: (4, 2)
    }

    mod_types = {
        page.MOD_ATTRIBUTES: msg.PDF_ATTRIBUTES,
        page.MOD_TRAITS: msg.PDF_TRAITS,
        page.MOD_SKILLS: msg.PDF_SKILLS,
        page.MOD_EQUIPMENT: msg.PDF_EQUIPMENT,
        page.MOD_WEAPONS: msg.PDF_WEAPONS,
        page.MOD_CONTACTS: msg.PDF_CONTACTS,
        page.MOD_EWT: msg.PDF_EWT,
        page.MOD_IMAGE: msg.PDF_IMAGE,
        page.MOD_NOTES: msg.PDF_NOTES
    }

    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.style = app.style
        self.char = app.char
        self.open_windows = app.open_windows
        self.widgets = {}

        self.template = None
        self.grid = []

        self.active_page = 1
        self.pages = 0

        self._getTemplate()
        if self.template is None:
            self.template = self._newTemplate()

        self.pages = len(self.template.findall("page"))
        
        # for display .. 
        self.cur_page = tk.StringVar()
        page_label = "{page} / {pages}".format(
            page=str(self.active_page),
            pages=str(self.pages)
        )
        self.cur_page.set(page_label)

        self.center_frame = tk.Frame(self)
        
        self.page_frame = tk.Frame(self.center_frame)
        self.showPage(self.page_frame)
        self.page_frame.pack(fill=tk.BOTH)
        self.control_frame = tk.Frame(self.center_frame)
        self.showControl(self.control_frame)
        self._switchPage(0)
        self.control_frame.pack(fill=tk.BOTH)
        self.center_frame.pack()

    def showPage(self, frame):
        cur_page = self.template.find("page[@num='"+str(self.active_page)+"']")
        self._generateGrid()
        for row in range(4):    
            for col in range(4):
                id = str(self.grid[self.active_page-1][col][row])
                position = str(col) + " " + str(row)
                text = msg.SL_EMPTY
                text_col = "#dddddd"
                module = cur_page.find("module[@id='"+id+"']")
                slot = tk.Canvas(
                    frame,
                    width=195,
                    height=120,
                    borderwidth=0,
                    highlightthickness=0,
                    relief=tk.RIDGE,
                    bg="#ffffff")
                self.widgets[position] = slot

                # display module ... 
                if module is not None:

                    # coordinates for a small module poly ... 
                    x1 = 4
                    y1 = 4
                    x2 = 191
                    y2 = 116
                    r = 4

                    # retrieve position and dimensions of module ... 
                    m_row = int(module.get("row"))
                    m_col = int(module.get("col"))
                    m_size = module.get("size")
                    m_rows = self.sizes[m_size][0] - 1
                    m_cols = self.sizes[m_size][1] - 1

                    # stretch box ... vertical
                    if row > m_row:
                        y1 -= 20
                    if row < m_row + m_rows:
                        y2 += 20

                    # stretch box ... horizontal
                    if col > m_col:
                        x1 -= 20
                    if col < m_col + m_cols:
                        x2 += 20

                    if row == m_row and col == m_col:
                        text = self._text(module)
                        text_col = "#000000"
                        
                    else:
                        text = ""

                    # draw box ...
                    self.drawPoly(slot, x1, y1, x2, y2, r)

                # generate the module crosses ...    
                slot.create_line(0, 0, 5, 0, fill="#dddddd")
                slot.create_line(0, 0, 0, 5, fill="#dddddd")
                slot.create_line(145, 0, 150, 0, fill="#dddddd")
                slot.create_line(0, 95, 0, 100, fill="#dddddd")

                # render text ... 
                slot.create_text(
                    97,
                    60,
                    text=text,
                    justify=tk.CENTER,
                    fill=text_col
                )

                # place canvas ...                 
                slot.grid(row=row, column=col)
                slot.bind(
                    "<Button-1>",
                    lambda event, position=position:
                        self._editModule(position)
                )

    def showControl(self, frame):

        tpl_ops = [
            (msg.SL_TT_NEW, "img/tpl_new.png", self._newTemplate),
            (msg.SL_TT_LOAD, "img/tpl_load.png", self._loadTemplate),
            (msg.SL_TT_SAVE, "img/tpl_save.png", self._saveTemplate)
        ]

        tpl = tk.LabelFrame(frame, text="Template")
        for op in tpl_ops:
            img = ImageTk.PhotoImage(file=op[1])
            button = tk.Button(
                tpl,
                text=op[0],
                image=img,
                command=op[2],
            )
            tt = ToolTip(button, op[0])
            button.image = img
            button.pack(side=tk.LEFT)
        tpl.pack(side=tk.LEFT)

        tk.Label(frame, text=" ").pack(side=tk.LEFT)

        flip = tk.LabelFrame(frame, text="blättern")
        icon = ImageTk.PhotoImage(file="img/book_previous.png")
        self.widgets["last_page"] = tk.Button(
            flip,
            image=icon,
            command=lambda:
                self._switchPage(-1)
        )
        ToolTip(self.widgets["last_page"], msg.SL_TT_LAST)
        self.widgets["last_page"].image = icon
        self.widgets["last_page"].pack(side=tk.LEFT, fill=tk.X)
        
        self.widgets["cur_page"] = tk.Label(
            flip,
            textvariable=self.cur_page
        )
        self.widgets["cur_page"].pack(side=tk.LEFT, fill=tk.X)

        icon = ImageTk.PhotoImage(file="img/book_next.png")
        self.widgets["next_page"] = tk.Button(
            flip,
            image=icon,
            command=lambda:
                self._switchPage(+1)
        )
        self.widgets["next_page"].image = icon
        ToolTip(self.widgets["next_page"], msg.SL_TT_NEXT)
        self.widgets["next_page"].pack(side=tk.LEFT, fill=tk.X)
        flip.pack(side=tk.LEFT)

        tk.Label(frame, text=" ").pack(side=tk.LEFT)

        pages = tk.LabelFrame(frame, text="Seiten")
        icon = ImageTk.PhotoImage(file="img/page_new.png")
        self.widgets["new_page"] = tk.Button(
            pages,
            image=icon,
            command=self._newPage
        )
        self.widgets["new_page"].image = icon
        ToolTip(self.widgets["new_page"], msg.SL_TT_NEW_PAGE)
        self.widgets["new_page"].pack(side=tk.LEFT)

        icon = ImageTk.PhotoImage(file="img/page_up.png")
        self.widgets["page_up"] = tk.Button(
            pages,
            image=icon,
            command=lambda:
                self._movePage(self.active_page-1)
        )
        self.widgets["page_up"].image = icon
        ToolTip(self.widgets["page_up"], msg.SL_TT_MOVE_UP)
        self.widgets["page_up"].pack(side=tk.LEFT)

        icon = ImageTk.PhotoImage(file="img/page_down.png")
        self.widgets["page_down"] = tk.Button(
            pages,
            image=icon,
            command=lambda:
            self._movePage(self.active_page+1)
        )
        self.widgets["page_down"].image = icon
        ToolTip(self.widgets["page_down"], msg.SL_TT_MOVE_DOWN)
        self.widgets["page_down"].pack(side=tk.LEFT)

        icon = ImageTk.PhotoImage(file="img/page_del.png")
        self.widgets["del_page"] = tk.Button(
            pages,
            image=icon,
            command=self._deletePage
        )
        self.widgets["del_page"].image = icon
        ToolTip(self.widgets["del_page"], msg.SL_TT_DEL_PAGE)
        self.widgets["del_page"].pack(side=tk.LEFT)
        pages.pack(side=tk.LEFT)

        tk.Label(frame, text=" ").pack(side=tk.LEFT)

        style_frame = tk.LabelFrame(frame, text=msg.SL_STYLE)
        s_icon = ImageTk.PhotoImage(file="img/style_straight.png")
        if self.template.getroot().get("style") == "straight":
            s_icon = ImageTk.PhotoImage(file="img/style_straight_sel.png")
        self.widgets["straight"] = straight_button = tk.Button(
            style_frame,
            image=s_icon,
            command=lambda: self._setStyle("straight")
        )
        ToolTip(straight_button, msg.SL_TT_STYLE_STRAIGHT)
        straight_button.image = s_icon
        straight_button.pack(side=tk.LEFT)
        r_icon = ImageTk.PhotoImage(file="img/style_round.png")
        if self.template.getroot().get("style") == "round":
            r_icon = ImageTk.PhotoImage(file="img/style_round_sel.png")
        self.widgets["round"] = round_button = tk.Button(
            style_frame,
            image=r_icon,
            command=lambda: self._setStyle("round")
        )
        ToolTip(round_button, msg.SL_TT_STYLE_ROUND)
        round_button.image = r_icon
        round_button.pack(side=tk.LEFT)
        style_frame.pack(side=tk.LEFT)

        img = ImageTk.PhotoImage(file="img/pdf.png")
        export = tk.Button(
            frame,
            text=msg.SL_EXPORT,
            image=img,
            compound=tk.LEFT,
            command=self._exportPDF
        )
        export.image = img
        export.pack(fill=tk.BOTH, expand=1)

    # switch active page ...
    def _switchPage(self, value, goto=False):
        """ This method takes the user to another page ... 
        value: int - ...
        goto: True - go to page specified by value
        goto: False - flip by value pages ... 
        """

        if goto: 
            active_page = value
        else:
            delta = value
            active_page = self.active_page + delta

        # make sure the page is valid
        if 1 <= active_page <= self.pages:
            # apply page
            self.active_page = active_page

            # set button state if on first or last page ...
            if active_page == 1: 
                self.widgets["last_page"].config(state=tk.DISABLED)
                self.widgets["page_up"].config(state=tk.DISABLED)
            else:  
                self.widgets["last_page"].config(state=tk.NORMAL)
                self.widgets["page_up"].config(state=tk.NORMAL)
            
            if active_page == self.pages: 
                self.widgets["next_page"].config(state=tk.DISABLED)
                self.widgets["page_down"].config(state=tk.DISABLED)
            else:  
                self.widgets["next_page"].config(state=tk.NORMAL)
                self.widgets["page_down"].config(state=tk.NORMAL)

            if self.pages == 1:
                self.widgets["del_page"].config(state=tk.DISABLED)
            else:    
                self.widgets["del_page"].config(state=tk.NORMAL)

            # show page
            self.showPage(self.page_frame)
            
            # update page display
            page_label = "{page} / {pages}".format(
                page=str(self.active_page),
                pages=str(self.pages)
            )
            self.cur_page.set(page_label)

    # append a new page at the end ... 
    def _newPage(self):
        self.pages += 1
        template = self.template.getroot()
        et.SubElement(template, "page", {"num": str(self.pages)})
        self._generateGrid()
        self._switchPage(self.pages - self.active_page)

    # move page
    def _movePage(self, num):
        if 1 <= num <= self.pages:
            search = "page[@num='"+str(num)+"']"
            other_page = self.template.find(search)
            search = "page[@num='"+str(self.active_page)+"']"
            active_page = self.template.find(search)

            other_page.set("num", str(self.active_page))
            active_page.set("num", str(num))

            self._refactorTemplate()
            self._switchPage(num, goto=True)

    # this deletes the current page from the template
    def _deletePage(self):
        cur_page = self.template.find("page[@num='"+str(self.active_page)+"']")
        template = self.template.getroot()
        template.remove(cur_page)
        
        if self.active_page < self.pages:
            for page_num in range(self.active_page+1, self.pages+1):
                cur_page = self.template.find("page[@num='"+str(page_num)+"']")
                cur_page.set("num", str(page_num-1))

            self.pages = len(self.template.findall("page"))
            self._refactorTemplate()
            self._switchPage(0)

        else:
            self.pages = len(self.template.findall("page"))
            self._switchPage(-1)

    # sorting pages and modules in the xml file ... 
    def _refactorTemplate(self):
        pages = self.template.findall("page")
        page_sorter = []
        for page in pages:
            modules = page.findall("module")
            module_sorter = []
            for module in modules:
                module_sorter.append(
                    (module.get("col")+module.get("row"), module)
                )
                
            module_sorter.sort()
            print(module_sorter)
            page[:] = [item[-1] for item in module_sorter]
            page_sorter.append((int(page.get("num")), page))
        page_sorter.sort()
        template = self.template.getroot()
        template[:] = [item[-1] for item in page_sorter]

    # call the PDF exporter (file selector)
    def _exportPDF(self):
        self.app.exportCharWindow(self.template)

    def _text(self, module):
        """ create the descriptive text """
        mod_type = module.get("type")
        text = self.mod_types[mod_type]

        params = module.findall("param")

        if mod_type == page.MOD_TRAITS:
            trait_type = None
            for param in params:
                if param.get("name", "") == "trait_type":
                    trait_type = param.get("value")
            if trait_type:
                trait_dict = {
                    "all": msg.PDF_ALL_TRAITS,
                    "positive": msg.PDF_POSITIVE_TRAITS,
                    "negative": msg.PDF_NEGATIVE_TRAITS
                }
                text = trait_dict.get(trait_type)

        if mod_type == page.MOD_SKILLS:
            skill_type = None
            for param in params:
                if param.get("name", "") == "skill_type":
                    skill_type = param.get("value")
            if skill_type:
                skill_dict = {
                    "all": msg.PDF_SKILLS_ALL,
                    "active": msg.PDF_SKILLS_ACTIVE,
                    "passive": msg.PDF_SKILLS_PASSIVE,
                    "knowledge": msg.PDF_SKILLS_KNOWLEDGE,
                    "lang": msg.PDF_SKILLS_LANGUAGE
                }

                text = skill_dict[skill_type]

        if mod_type == page.MOD_EQUIPMENT:
            item_id = None
            condensed = None
            equipped = None
            content = None

            for param in params:
                if param.get("name", "") == "item_id":
                    item_id = param.get("value", "")
                if param.get("name", "") == "condensed":
                    condensed = True
                if param.get("name", "") == "equipped":
                    equipped = True
                if param.get("name", "") == "content":
                    content = True

            if item_id:
                item = self.char.getItemById(item_id)
                if item is not None:
                    text = msg.ME_CONTENTS + "\n" + item.get("name")
            elif condensed:
                text += "\n" + msg.ME_CONDENSED
            if equipped:
                text = msg.ME_EQUIPPED + "\n" + text
            if content:
                text += "\n" + msg.ME_BAG_CONTENTS

        if mod_type == page.MOD_WEAPONS:
            variant = None
            equipped = None
            for param in params:
                if param.get("name", "") == "variant":
                    variant = param.get("value")
                if param.get("name", "") == "equipped":
                    equipped = True

            if variant:
                weapons_dict = {
                    "all": msg.PDF_ALL_WEAPONS,
                    "melee": msg.PDF_MELEE,
                    "guns": msg.PDF_GUNS,
                    "ammo": msg.PDF_AMMO
                }
                text = weapons_dict[variant]

            if equipped:
                text += "\n" + msg.ME_JUST_EQUIPPED

        if mod_type == page.MOD_NOTES:
            id = None
            for param in params:
                if param.get("name", "") == "note_id":
                    id = param.get("value")
            if id:
                note = self.char.findNoteById(id)
                if note is not None:
                    text += ":\n" + note.get("name")

        return text

    # open an edit window
    def _editModule(self, position):
        if self.app.open_windows["mod_ed"] != 0: 
            self.app.open_windows["mod_ed"].close()
        ModuleEditor(self, position)

    # retrieve the highest given module id ...     
    def getHighestModuleId(self):
        modules = self.template.findall(".//module")
        id = 0
        for module in modules:
            module_id = int(module.get("id", "0"))
            if module_id > id: 
                id = module_id
        return id
                
    def addModule(self, module):
        page = self.template.find("page[@num='"+str(self.active_page)+"']")
        page.append(module)
        self._generateGrid()

    # create a new element tree
    def _newTemplate(self):
        template = et.Element("template")
        et.SubElement(template, "page", {"num":"1"})
        template = et.ElementTree(template)
        if self.template is not None:
            self.template = template
            self.pages = 1
            self.active_page = 1
            self._switchPage(1, goto=True)
        else:
            return template

    def _setStyle(self, style=None):
        if not style:
            return
        if style == "round":
            r_icon = ImageTk.PhotoImage(file="img/style_round_sel.png")
            s_icon = ImageTk.PhotoImage(file="img/style_straight.png")
            self.widgets["round"].config(image=r_icon)
            self.widgets["round"].image = r_icon
            self.widgets["straight"].config(image=s_icon)
            self.widgets["straight"].image = s_icon
        if style == "straight":
            r_icon = ImageTk.PhotoImage(file="img/style_round.png")
            s_icon = ImageTk.PhotoImage(file="img/style_straight_sel.png")
            self.widgets["round"].config(image=r_icon)
            self.widgets["round"].image = r_icon
            self.widgets["straight"].config(image=s_icon)
            self.widgets["straight"].image = s_icon
        root = self.template.getroot()
        root.set("style", style)

    # load a template from disk ... 
    def _loadTemplate(self):
        options = {
            'defaultextension': '.xml',
            'filetypes': [('Template', '.xml')],
            'initialdir': './templates',
            'initialfile': 'template.xml',
            'parent': self,
            'title': 'Charakterbogentemplate laden ...',
        }
        filename = tkfd.askopenfilename(**options)
        if filename:
            with open(filename, mode="rb") as file:
                self.char.setPDFTemplate(filename)
                self.template = et.parse(file)
                self.pages = len(self.template.findall("page"))
                self._generateGrid()
                self._switchPage(0)
        else:
            pass

    def _getTemplate(self):
        filename = self.char.getPDFTemplate()
        print(filename)
        if filename:
            with open(filename, mode="rb") as file:
                self.template = et.parse(file)
                self._generateGrid()
                self._switchPage(0)

    # save the current template to disk ... 
    def _saveTemplate(self):
        suggested_filename = "character.xml"
        options = { 
            "defaultextension": ".xml",
            "filetypes": [("Template", ".xml")],
            "initialdir": "./templates",
            "initialfile": "template.xml",
            "parent": self,
            "title": "Charakterbogentemplate speichern ...",
        }
        filename = tkfd.asksaveasfilename(**options)
        if filename:
            with open(filename, mode="wb") as file:
                self.template.write(
                    file,
                    encoding="utf-8",
                    xml_declaration=True
                )
                self.char.setPDFTemplate(filename)

    def _generateGrid(self):
        self.grid = []
        pages = self.template.findall("page")
        for mypage in pages:
            page_num = int(mypage.get("num", "0"))
            page_grid = [[0, 0, 0, 0] for i in range(4)]
            modules = mypage.findall("module")
            for module in modules: 
                size = module.get("size")
                id = module.get("id")
                row = int(module.get("row"))
                col = int(module.get("col"))
                rows = 1
                cols = 1
                if size == page.DOUBLE:
                    rows = 2
                elif size == page.TRIPLE:
                    rows = 3
                elif size == page.FULL:
                    rows = 4
                elif size == page.WIDE:
                    rows = 1
                    cols = 2
                elif size == page.QUART:
                    rows = 2
                    cols = 2
                elif size == page.BIG:
                    rows = 3
                    cols = 2
                elif size == page.HALF:
                    rows = 4
                    cols = 2
                
                for c in range(col, col+cols):
                    for r in range(row, row+rows):
                        page_grid[c][r] = int(id)

            self.grid.append(page_grid)

    @staticmethod
    def drawPoly(canvas, x1, y1, x2, y2, r):
        canvas.create_polygon(
            x1, y1 + 2 * r,  # corner 1
            x1, y1 + 2 * r,
            x1, y1 + r,
            x1 + r, y1,
            x1 + 2 * r, y1,
            x1 + 2 * r, y1,
            x2 - 2 * r, y1,  # corner 2
            x2 - 2 * r, y1,
            x2 - r, y1,
            x2, y1 + r,
            x2, y1 + 2 * r,
            x2, y1 + 2 * r,
            x2, y2 - 2 * r,  # corner 3
            x2, y2 - 2 * r,
            x2, y2 - r,
            x2 - r, y2,
            x2 - 2 * r, y2,
            x2 - 2 * r, y2,
            x1 + 2 * r, y2,  # corner 4
            x1 + 2 * r, y2,
            x1 + r, y2,
            x1, y2 - r,
            x1, y2 - 2 * r,
            x1, y2 - 2 * r,
            smooth=1,
            fill="#ffffff",
            outline="#000000",
            width=2
        )
