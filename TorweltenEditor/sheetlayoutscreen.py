# coding=utf-8

import xml.etree.ElementTree as et
import tkinter.filedialog as tkfd
from moduleeditor import ModuleEditor
from PIL import ImageTk, Image, PngImagePlugin
import tkinter as tk
import config
page = config.Page()
msg = config.Messages()


class LayoutScreen(tk.Frame):

    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.char = app.char
        self.open_windows = app.open_windows
        
        self.sizes = {
            page.SINGLE: (1, 1),
            page.DOUBLE: (2, 1),
            page.TRIPLE: (3, 1),
            page.FULL: (4, 1),
            page.WIDE: (1, 2),
            page.QUART: (2, 2),
            page.BIG: (3, 2),
            page.HALF: (4, 2)
        }

        self.mod_types = {
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

        self.template = None
        self.template = self._newTemplate()
        
        self.active_page = 1
        self.pages = len(self.template.findall("page"))
        
        # for display .. 
        self.cur_page = tk.StringVar()
        page_label = "{page} / {pages}".format(
            page=str(self.active_page),
            pages=str(self.pages)
        )
        self.cur_page.set(page_label)
        
        self.grid = []
        self.widgets = {}
        
        self.toolbar = tk.Frame(self)
        self.showToolbar(self.toolbar)

        self.toolbar.pack(fill=tk.X)
        self.center_frame = tk.Frame(self)
        
        self.page_frame = tk.Frame(self.center_frame)
        self.showPage(self.page_frame)
        self.page_frame.pack(fill=tk.BOTH)
        self.control_frame = tk.Frame(self.center_frame)
        self.showControl(self.control_frame)
        self._switchPage(0)
        self.control_frame.pack(fill=tk.BOTH)
        self.center_frame.pack()

    def showToolbar(self, frame):
        new_template = tk.Button(
            frame,
            text=msg.SL_NEW,
            command=self._newTemplate
        )
        new_template.pack(side=tk.LEFT)
        load_template = tk.Button(
            frame,
            text=msg.SL_LOAD,
            command=self._loadTemplate
        )
        load_template.pack(side=tk.LEFT)
        save_template = tk.Button(
            frame,
            text=msg.SL_SAVE,
            command=self._saveTemplate
        )
        save_template.pack(side=tk.LEFT)

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
                    width=150,
                    height=100,
                    borderwidth=0,
                    highlightthickness=0,
                    relief=tk.RIDGE,
                    bg="#ffffff")
                self.widgets[position] = slot

                # display module ... 
                if module is not None:
                    mod_type = module.get("type")

                    # coordinates for a small module poly ... 
                    x1 = 4
                    y1 = 4
                    x2 = 146
                    y2 = 96
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
                        text = self.mod_types[mod_type]
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
                slot.create_text(75, 50, text=text, fill=text_col)

                # place canvas ...                 
                slot.grid(row=row, column=col)
                slot.bind(
                    "<Button-1>",
                    lambda event, position=position:
                        self._editModule(position)
                )

    def showControl(self, frame):
        sub_frame = tk.Frame(frame)
        icon = ImageTk.PhotoImage(file="ui_img/book_previous.png")
        self.widgets["last_page"] = tk.Button(
            sub_frame,
            image=icon,
            command=lambda:
                self._switchPage(-1)
        )
        self.widgets["last_page"].image = icon
        self.widgets["last_page"].pack(side=tk.LEFT, fill=tk.X)
        
        self.widgets["cur_page"] = tk.Label(
            sub_frame,
            textvariable=self.cur_page
        )
        self.widgets["cur_page"].pack(side=tk.LEFT, fill=tk.X)

        icon = ImageTk.PhotoImage(file="ui_img/book_next.png")
        self.widgets["next_page"] = tk.Button(
            sub_frame,
            image=icon,
            command=lambda:
                self._switchPage(+1)
        )
        self.widgets["next_page"].image = icon
        self.widgets["next_page"].pack(side=tk.LEFT, fill=tk.X)

        icon = ImageTk.PhotoImage(file="ui_img/page_new.png")
        self.widgets["new_page"] = tk.Button(
            sub_frame,
            image=icon,
            command=self._newPage
        )
        self.widgets["new_page"].image = icon
        self.widgets["new_page"].pack(side=tk.LEFT)

        icon = ImageTk.PhotoImage(file="ui_img/page_up.png")
        self.widgets["page_up"] = tk.Button(
            sub_frame,
            image=icon,
            command=lambda:
                self._movePage(self.active_page-1)
        )
        self.widgets["page_up"].image = icon
        self.widgets["page_up"].pack(side=tk.LEFT)

        icon = ImageTk.PhotoImage(file="ui_img/page_down.png")
        self.widgets["page_down"] = tk.Button(
            sub_frame,
            image=icon,
            command=lambda:
            self._movePage(self.active_page+1)
        )
        self.widgets["page_down"].image = icon
        self.widgets["page_down"].pack(side=tk.LEFT)

        icon = ImageTk.PhotoImage(file="ui_img/page_del.png")
        self.widgets["del_page"] = tk.Button(
            sub_frame,
            image=icon,
            command=self._deletePage
        )
        self.widgets["del_page"].image = icon
        self.widgets["del_page"].pack(side=tk.LEFT)

        sub_frame.pack(fill=tk.X, expand=1)

        export = tk.Button(
            frame,
            text=msg.SL_EXPORT,
            command=self._exportPDF
        )
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
        file = tkfd.askopenfile(mode="rb", **options)
        if file:
            self.template = et.parse(file)
            file.close()
            self.pages = len(self.template.findall("page"))
            self._generateGrid()
            self._switchPage(0)
        else:
            pass

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
        file = tkfd.asksaveasfile(mode="wb", **options)
        if file:
            self.template.write(file, encoding="utf-8", xml_declaration=True)
            file.close()
 
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
