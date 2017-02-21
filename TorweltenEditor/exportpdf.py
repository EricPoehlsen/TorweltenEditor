# coding=utf-8

import config
import os
from threading import Thread
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm 
from reportlab.pdfbase import pdfmetrics  
from reportlab.pdfbase.ttfonts import TTFont  
from reportlab.lib.utils import ImageReader
from reportlab import rl_settings,rl_config

from PIL import Image,PngImagePlugin,JpegImagePlugin
import tkinter as tk

page_data = config.Page()
SINGLE = page_data.SINGLE
DOUBLE = page_data.DOUBLE
TRIPLE = page_data.TRIPLE
FULL = page_data.FULL
WIDE = page_data.WIDE
QUART = page_data.QUART
BIG = page_data.BIG
HALF = page_data.HALF

SINGLE_WIDTH = page_data.SINGLE_WIDTH
DOUBLE_WIDTH = page_data.DOUBLE_WIDTH
SINGLE_HEIGHT = page_data.SINGLE_HEIGHT
DOUBLE_HEIGHT = page_data.DOUBLE_HEIGHT
TRIPLE_HEIGHT = page_data.TRIPLE_HEIGHT
FULL_HEIGHT = page_data.FULL_HEIGHT
        
BAR_WIDTH = page_data.BAR_WIDTH
OUTER_RADIUS = page_data.OUTER_RADIUS
INNER_RADIUS = page_data.INNER_RADIUS
Y_PADDING = page_data.Y_PADDING
FONT_NAME = "samuel"

SPACER = page_data.SPACER
MINLINE_HEIGHT = page_data.MINLINE_HEIGHT
INFO_LINE = page_data.INFO_LINE
STROKE = page_data.STROKE

X_ORIGINS = [14, 221, 428, 635]
Y_ORIGINS = [580, 435, 290, 145]

msg = config.Messages()
it = config.ItemTypes()


class DisplayPdf(Thread):
    def __init__(self, filename, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.filename = filename

    def run(self):
        # display the pdf ...
        os.system('"' + self.filename + '"')


class ExportPdf:
    # defining some constants in points ... 

    def __init__(self, filename, char, traits, template):
        self.char = char
        self.traits = traits
        self.filename = filename
        self.template = template

        self.pdf = self.start()
        
        samuel = "fonts/hh_samuel.ttf"
        pdfmetrics.registerFont(TTFont(FONT_NAME, samuel)) 

        if self.template is not None:
            pages = self.template.findall("page")
            for page in pages: 
                self.renderPage(self.pdf, page)
                self.nextPage(self.pdf)
        else: 
            self.renderStandard()
            self.nextPage(self.pdf)
        
        self.save(self.pdf)
        self.display()
    
    # begin generation of a new pdf            
    def start(self):
        return canvas.Canvas(self.filename, pagesize=landscape(A4))

    # store page - next page
    @staticmethod
    def nextPage(canvas):
        canvas.showPage()

    # write file
    @staticmethod
    def save(canvas):
        canvas.save()
        pass

    # open pdf in os 
    def display(self):
        thread = DisplayPdf(self.filename)
        thread.start()

    # this renders a page template
    def renderPage(self, canvas, page):
        if page is not None:
            modules = page.findall("module")
            for module in modules: 
                kwargs = {}
                col = int(module.get("col"))
                row = int(module.get("row"))
                size = module.get("size")
                mod_type = module.get("type")
                kwargs["canvas"] = canvas
                kwargs["x"] = X_ORIGINS[col]
                kwargs["y"] = Y_ORIGINS[row]
                kwargs["size"] = size
                other_params = module.findall("param")
                for param in other_params:
                    name = param.get("name")
                    value = param.get("value")
                    kwargs[name] = value

                if mod_type == page_data.MOD_ATTRIBUTES:
                    self.moduleAttributes(**kwargs)
                elif mod_type == page_data.MOD_TRAITS:
                    self.moduleTraits(**kwargs)
                elif mod_type == page_data.MOD_SKILLS:
                    self.moduleSkills(**kwargs)
                elif mod_type == page_data.MOD_WEAPONS:
                    self.moduleWeapons(**kwargs)
                elif mod_type == page_data.MOD_EQUIPMENT:
                    self.moduleEquipment(**kwargs)
                elif mod_type == page_data.MOD_CONTACTS:
                    self.moduleContacts(**kwargs)
                elif mod_type == page_data.MOD_NOTES:
                    self.moduleNotes(**kwargs)
                elif mod_type == page_data.MOD_EWT:
                    self.moduleEWT(**kwargs)
                elif mod_type == page_data.MOD_IMAGE:
                    self.moduleImage(**kwargs)

    # standard one page sheet ... 
    def renderStandard(self):
        self.moduleAttributes(
            self.pdf,
            X_ORIGINS[0],
            Y_ORIGINS[0],
            size=DOUBLE
        )
        self.moduleTraits(
            self.pdf,
            X_ORIGINS[1],
            Y_ORIGINS[0],
            size=DOUBLE
        )
        self.moduleSkills(
            self.pdf,
            X_ORIGINS[0],
            Y_ORIGINS[2],
            size=DOUBLE,
            skill_type="active"
        )
        self.moduleSkills(
            self.pdf,
            X_ORIGINS[1],
            Y_ORIGINS[2],
            DOUBLE,
            skill_type="passive"
        )
        self.moduleWeapons(
            self.pdf,
            X_ORIGINS[2],
            Y_ORIGINS[0],
            size=DOUBLE,
            variant="guns",
            info_lines=3
        )
        self.moduleWeapons(
            self.pdf,
            X_ORIGINS[2],
            Y_ORIGINS[2],
            variant="melee",
            info_lines=1
        )
        self.moduleEWT(
            self.pdf,
            X_ORIGINS[2],
            Y_ORIGINS[3]
        )
        self.moduleEquipment(
            self.pdf,
            X_ORIGINS[3],
            Y_ORIGINS[0],
            size=DOUBLE,
            condensed=True
        )
        self.moduleContacts(
            self.pdf,
            X_ORIGINS[3],
            Y_ORIGINS[2],
            size=DOUBLE
        )

    def drawTitle(self, canvas, x, y, height, title):
        """ this draws the title bar and places the text at the correct location ...
        canvas: reportlab canvas
        x,y: top,left coordinates in points
        height: height in points
        title: string - text to display
        """
        
        bar = BAR_WIDTH
        i_rad = INNER_RADIUS
        stroke = STROKE

        canvas.setFillColorRGB(1, 1, 1)
        canvas.roundRect(x, (y+2-height), bar, height-4, i_rad, stroke, 1)

        canvas.saveState()
        canvas.setFillColorRGB(0, 0, 0)
        canvas.rotate(90)
        canvas.setFont(FONT_NAME, 18)
        canvas.drawRightString(y-4, -x-bar+3, title)
        canvas.rotate(-90)
        canvas.restoreState()

    def moduleAttributes(self, canvas, x, y, size="double"):
        """ this module draws a box with attributes
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "double"
        CURRENTLY ONLY double EXISTS
        """

        # localize variables for easy use ... 
        width = SINGLE_WIDTH

        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING

        stroke = STROKE
        bar = BAR_WIDTH
        info_line = INFO_LINE

        title = "ATTRIBUTE"

        # handle different sizes
        if size == DOUBLE: 
            height = DOUBLE_HEIGHT
        else:
            valid_sizes = [DOUBLE]
            raise TypeError("size: " + ",".join(valid_sizes))

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(x, (y-height), width, height, o_rad, stroke, 1)

        self.drawTitle(canvas, x, y, height, title)
        
        if size == DOUBLE:
            inner_height = height - 2*padding
            inner_width = width - bar
            canvas.setFillColorRGB(1, 1, 1)
            local_x = x + bar
            local_y = y - inner_height - padding
            canvas.roundRect(
                local_x,
                local_y,
                inner_width,
                inner_height,
                i_rad,
                1,
                1
            )
            canvas.rect(x+width - 3, y-height+3, 6, height - 6, 0, 1)
            # draw the vitals ...
            vitals = ["lp", "ep", "mp"]
            vit_width = 30
            vit_count = 3
            box_dims = vit_width * 1.0 / 2
            tag_height = box_dims
            tag_text_size = tag_height - 3
            small_box_dims = vit_width * 1.0 / 5
            local_height = 10.0*box_dims + tag_height + 2.0*small_box_dims + 2*padding
            
            for vital in vitals:
            
                local_x = x + width - vit_count*vit_width
                local_y = y - height
                
                canvas.setFillColorRGB(0, 0, 0)
                canvas.roundRect(
                    local_x + box_dims/2,
                    local_y,
                    box_dims,
                    local_height ,
                    o_rad,
                    1,
                    1
                )
                lower_box_height = 2*padding + 2*small_box_dims + tag_height
                canvas.roundRect(
                    local_x,
                    local_y,
                    vit_width,
                    lower_box_height,
                    o_rad,
                    1,
                    1
                )

                canvas.setFillColorRGB(1, 1, 1)

                for i in range(10):
                    local_y = y - (height-local_height) - padding - (i+1)*box_dims
                    canvas.roundRect(
                        local_x+box_dims/2,
                        local_y,
                        box_dims,
                        box_dims,
                        i_rad,
                        1,
                        1
                    )
                local_y -= tag_height
                canvas.setFillColorRGB(1, 1, 1)
                canvas.roundRect(
                    local_x,
                    local_y,
                    vit_width,
                    tag_height,
                    i_rad,
                    1,
                    1
                )
                canvas.setFillColorRGB(0, 0, 0)
                canvas.setFont(FONT_NAME, tag_text_size)
                value = self.char.getAttributeValue(vital)
                text = vital.upper()
                if value != 0:
                    text += ": " + str(value)
                else:
                    text += ":    "
                canvas.drawCentredString(
                    local_x + vit_width/2,
                    local_y+2,
                    text
                )
                
                local_y -= small_box_dims
                canvas.setFillColorRGB(1, 1, 1)
                for col in range(5):
                    for row in range(2):
                        canvas.roundRect(
                            local_x+col*small_box_dims,
                            local_y-row*small_box_dims,
                            small_box_dims,
                            small_box_dims,
                            1,
                            1,
                            1
                        )
                vit_count -= 1

            # draw the other attribs
            attribs = ["phy", "men", "soz", "nk", "fk"]

            line_height = tag_height
            text_size = tag_text_size
            scale_width = inner_width - 3.0*vit_width
            att_col = 1.0 * vit_width - 5
            val_col = (1.0 * scale_width - att_col) / 11

            # draw outer_box ...
            bounding_width = att_col + 10.0 * val_col + bar 
            bounding_height = len(attribs) * line_height + 2*padding
            local_x = x
            local_y = y-height
            canvas.setFillColorRGB(0, 0, 0)
            canvas.roundRect(
                local_x,
                local_y,
                bounding_width,
                bounding_height,
                o_rad,
                stroke,
                1
            )

            # draw attrib_lines ...
            i = len(attribs) - 1
            for attrib in attribs:
                local_x = x + bar
                local_y = y - height + i * line_height + padding
                canvas.setFillColorRGB(1, 1, 1)
                canvas.roundRect(
                    local_x,
                    local_y,
                    att_col,
                    line_height,
                    i_rad,
                    stroke,
                    1
                )
                canvas.setFont(FONT_NAME, text_size)
                canvas.setFillColorRGB(0, 0, 0)
                canvas.drawCentredString(
                    local_x + att_col / 2, 
                    local_y + 3,
                    attrib.upper()
                )
                
                attr_value = self.char.getAttributeValue(attrib)
                for value in range(10):
                    canvas.setFillColorRGB(1, 1, 1)
                    canvas.roundRect(
                        local_x + att_col + value*val_col,
                        local_y,
                        val_col,
                        line_height,
                        i_rad,
                        stroke,
                        1
                    )
                    if attr_value > value:
                        canvas.setFillColorRGB(0, 0, 0)
                        canvas.roundRect(
                            local_x + att_col + value*val_col + 1,
                            local_y + 1,
                            val_col - 2,
                            line_height - 2,
                            1,
                            0,
                            1
                        )
                i -= 1

        # draw character_data ...
        data_list_1 = [
            "name",
            "species",
            "origin",
            "concept",
            "player"
        ]
        data_list_2 = [
            "height",
            "weight",
            "age",
            "gender"
        ]
        data_list_3 = [
            "hair",
            "eyes",
            "skin",
            "skintype"
        ]

        data_names = {
            "name": msg.NAME,
            "species": msg.SPECIES,
            "origin": msg.ORIGIN,
            "concept": msg.CONCEPT,
            "player": msg.PLAYER,
            "height": msg.HEIGHT,
            "weight": msg.WEIGHT,
            "age": msg.AGE,
            "gender": msg.GENDER,
            "hair": msg.HAIR,
            "eyes": msg.EYES,
            "skin": msg.SKIN_COLOR,
            "skintype": msg.SKIN_TYPE
        }

        # get space
        data_height = inner_height - 6.3 * vit_width+2*padding
        data_width = inner_width / 5.0
        line_height = data_height / 5.0

        # set local positions
        local_x = x
        local_y = y - data_height - 2*padding
        offset = 1.5

        # draw border
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(
            local_x,
            local_y,
            width,
            data_height,
            o_rad,
            1,
            1
        )
        
        # draw contents ...
        info_font = 4 
        for i in range(5):
            local_x = x + bar
            local_y = y - padding - (i+1)*line_height
            # #draw the boxes ...
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(
                local_x,
                local_y,
                data_width*3,
                line_height,
                i_rad,
                1,
                1
            )
            canvas.setFillColorRGB(0, 0, 0)
            data = data_list_1[i]
            info_text = data_names[data]
            data_text = self.char.getData(data)
            canvas.setFontSize(info_font)
            canvas.drawString(local_x+offset, local_y+offset, info_text)
            canvas.setFontSize(line_height-3)
            canvas.drawString(local_x+offset*8, local_y+offset+1, data_text)

            if i < 4:
                canvas.setFillColorRGB(1, 1, 1)
                canvas.roundRect(
                    local_x+data_width*3,
                    local_y,
                    data_width,
                    line_height,
                    i_rad,
                    1,
                    1
                )
                canvas.roundRect(
                    local_x+data_width*4,
                    local_y,
                    data_width,
                    line_height,
                    i_rad,
                    1,
                    1
                )
                canvas.setFillColorRGB(0, 0, 0)

                data = data_list_2[i]
                info_text = data_names[data]
                data_text = self.char.getData(data)
                canvas.setFontSize(info_font)
                canvas.drawString(
                    local_x + data_width*3 + offset,
                    local_y + offset,
                    info_text
                )
                canvas.setFontSize(line_height-info_font-3)
                canvas.drawCentredString(
                    local_x+data_width*3.5,
                    local_y+offset+info_font+1,
                    data_text
                )

                data = data_list_3[i]
                info_text = data_names[data]
                data_text = self.char.getData(data)
                canvas.setFontSize(info_font)
                canvas.drawString(
                    local_x+data_width*4+offset,
                    local_y+offset,
                    info_text
                )
                canvas.setFontSize(line_height-info_font-3)
                canvas.drawCentredString(
                    local_x+data_width*4.5,
                    local_y+offset+info_font+1,
                    data_text
                )
            # xp box
            else:
                canvas.setFillColorRGB(1, 1, 1)
                canvas.roundRect(
                    local_x+data_width*3,
                    local_y,
                    data_width*2,
                    line_height,
                    i_rad,
                    1,
                    1
                )
                canvas.setFillColorRGB(0, 0, 0)
                canvas.setFontSize(info_font)
                canvas.drawString(
                    local_x+data_width*3+offset,
                    local_y+offset,
                    "XP"
                )
                xp_avail = self.char.getAvailableXP()
                xp_total = self.char.getTotalXP()
                canvas.setFontSize(line_height-3)
                xp_text = ""
                if xp_avail != xp_total:
                    xp_text = str(xp_avail) + " / " + str(xp_total)
                canvas.drawCentredString(
                    local_x+data_width*4,
                    local_y+offset+1,
                    xp_text
                )

        # draw image box
        local_x = x
        local_y = y - height + 2.75 * vit_width
        upper_y = y - height + 2*padding + 11*box_dims + 2*small_box_dims

        bounding_height = upper_y - local_y
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(
            local_x,
            local_y,
            bounding_width,
            bounding_height,
            o_rad,
            1,
            1
        )
        local_y += padding
        canvas.setFillColorRGB(1, 1, 1)
        img_width = bounding_width-bar
        img_height = bounding_height-2*padding
        canvas.roundRect(
            local_x+bar,
            local_y,
            img_width,
            img_height,
            i_rad,
            1,
            1
        )

        # get the image ...
        image = self._loadImage(size, img_width, img_height)

        # draw image ...
        if image is not None: 
            img = ImageReader(image)
            canvas.drawImage(
                img,
                local_x+bar,
                local_y,
                width=img_width,
                height=img_height,
                mask="auto")

        canvas.setFontSize(info_font)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(local_x+bar+offset, local_y+offset, "Bild")

        # draw title last ... for reasons :D
        self.drawTitle(canvas, x, y, height, title)

    def moduleNotes(
        self,
        canvas,
        x,
        y,
        size=SINGLE,
        lines_per_entry=1,
        title="NOTIZEN",
        info_title=None
    ):
        """ this module draws a generic box ... 
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "single", "wide, "double", "quart", "triple", "big", "full", "half"
        trait_type: string - "all", "positive", "negative"
        lines_per_entry: int - 0 (no lines) 
        title: string - name of box ... 
        info_title: String - Header Bar ...
        """

        # localize variables for easy use ... 
        limit = 52
        width = SINGLE_WIDTH
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING

        stroke = STROKE
        bar = BAR_WIDTH
        info_line = INFO_LINE

        # cleanup types ...
        lines_per_entry = int(lines_per_entry)

        wide = False
        # handle different sizes
        if size == SINGLE: 
            height = SINGLE_HEIGHT
        elif size == DOUBLE: 
            height = DOUBLE_HEIGHT
        elif size == TRIPLE: 
            height = TRIPLE_HEIGHT
        elif size == FULL: 
            width = SINGLE_WIDTH
        elif size == WIDE: 
            height = SINGLE_HEIGHT
            wide = True
        elif size == QUART: 
            height = DOUBLE_HEIGHT
            wide = True
        elif size == BIG: 
            height = TRIPLE_HEIGHT
            wide = True
        elif size == HALf:
            height = FULL_HEIGHT
            wide = True
        else:
            valid_sizes = [
                SINGLE,
                WIDE,
                DOUBLE,
                QUART,
                TRIPLE,
                BIG,
                FULL,
                HALF
            ]
            raise TypeError("size: " + ",".join(valid_sizes))

        if wide: 
            width = DOUBLE_WIDTH
            limit = 100
           
        if info_title is None:
            info_line = 0
        inner_height = height - 2*padding - info_line
        line_count = int(inner_height / MINLINE_HEIGHT)
        if lines_per_entry == 0 or lines_per_entry > line_count:
            lines_per_entry = line_count
        while line_count % lines_per_entry != 0:
            line_count -= 1
        line_height = 1.0 * inner_height / line_count

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(
            x,
            y-height,
            width,
            height,
            o_rad,
            stroke,
            1
        )
        
        title = title.upper()
        self.drawTitle(canvas, x, y, height, title)

        # the header line ...
        if info_title: 
            canvas.setFillColorRGB(1, 1, 1)
            local_x = x + bar
            local_y = y - padding - info_line
            canvas.roundRect(
                local_x,
                local_y,
                width-bar,
                info_line,
                i_rad,
                stroke,
                1
            )
            offset = 2
            canvas.setFillColorRGB(0, 0, 0)
            canvas.setFont(FONT_NAME, 7)
            canvas.drawString(local_x + offset, local_y+offset, info_title)
        
        canvas.setFillColorRGB(1, 1, 1)

        canvas.setFont(FONT_NAME, 10)

        offset = 3

        i = line_count - 1

        while i >= 0:
            # construct the line ... 
            i -= lines_per_entry
            local_y = (y + padding - height) + line_height * (i+1)
            local_x = (x + bar)

            # boxes
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(
                local_x,
                local_y,
                width-bar,
                line_height*lines_per_entry,
                i_rad,
                stroke,
                1
            )

    def moduleImage(self, canvas, x, y, size=SINGLE):
        """ this module draws a image box ...
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "single", "wide, "double", "quart", "triple", "big", "full", "half"
        """

        # localize variables for easy use ... 
        width = SINGLE_WIDTH
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING

        stroke = STROKE

        wide = False
        # handle different sizes
        if size == SINGLE: 
            height = SINGLE_HEIGHT
        elif size == DOUBLE: 
            height = DOUBLE_HEIGHT
        elif size == TRIPLE: 
            height = TRIPLE_HEIGHT
        elif size == FULL: 
            height = FULL_HEIGHT
        elif size == WIDE: 
            height = SINGLE_HEIGHT
            wide = True
        elif size == QUART: 
            height = DOUBLE_HEIGHT
            wide = True
        elif size == BIG: 
            height = TRIPLE_HEIGHT
            wide = True
        elif size == HALF: 
            height = FULL_HEIGHT
            wide = True
        else:
            valid_sizes = [
                SINGLE,
                WIDE,
                DOUBLE,
                QUART,
                TRIPLE,
                BIG,
                FULL,
                HALF
            ]
            raise TypeError("size: " + ",".join(valid_sizes))

        if wide: 
            width = DOUBLE_WIDTH

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(x, (y-height), width, height, o_rad, stroke, 1)
        
        # draw the inner box (so there is something white if the image has
        # transparency or there is no image
        canvas.setFillColorRGB(1, 1, 1)
        local_height = height - 2 * padding
        local_x = x
        local_y = y - padding
        canvas.roundRect(
            local_x,
            local_y-local_height,
            width,
            local_height,
            i_rad,
            stroke,
            1
        )

        # get the image ...
        image = self._loadImage(size, width, height)

        # draw image ...
        if image is not None: 
            img = ImageReader(image)
            canvas.drawImage(
                img,
                local_x,
                local_y - local_height,
                width=width - 1,
                height=local_height,
                mask="auto"
            )

            # brute forcing a nice border ... 
            canvas.setFillAlpha(0)
            canvas.roundRect(
                local_x,
                local_y-local_height-padding,
                width,
                local_height+(2*padding),
                o_rad,
                stroke,
                1
            )
            canvas.roundRect(
                local_x,
                local_y-local_height-(0.5*padding),
                width,
                local_height+padding,
                (0.5*(o_rad+i_rad)),
                stroke,
                1)
            canvas.roundRect(
                local_x,
                local_y-local_height,
                width,
                local_height,
                i_rad,
                stroke,
                1
            )
            canvas.setFillAlpha(1)

    def moduleTraits(
        self,
        canvas,
        x,
        y,
        size=SINGLE,
        trait_type="all",
        info_lines=1,
        start_index=0
    ):
        """ this module draws a box with the character traits
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "single", "double", "triple", "full"
        trait_type: string - "all", "positive", "negative"
        info_lines: int - number of info lines
        start_index: int - where to start in the skill list ...
        """

        # localize variables for easy use ... 
        width = SINGLE_WIDTH
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING

        stroke = STROKE
        bar = BAR_WIDTH
        info_line = INFO_LINE
        limit = 40

        # type cleanup ...
        info_lines = int(info_lines)
        start_index = int(start_index)

        # handle trait_type
        if trait_type == "all":
            title = msg.PDF_TRAITS.upper()
        elif trait_type == "positive":
            title = msg.PDF_POSITIVE_TRAITS.upper()
        elif trait_type == "negative":
            title = msg.PDF_NEGATIVE_TRAITS.upper()
        else:
            raise TypeError("Allowed trait_types: 'all','positive','negative'")

        wide = False
        # handle different sizes
        if size == SINGLE: 
            height = SINGLE_HEIGHT
        elif size == DOUBLE: 
            height = DOUBLE_HEIGHT
        elif size == TRIPLE: 
            height = TRIPLE_HEIGHT
        elif size == FULL: 
            height = FULL_HEIGHT
        elif size == WIDE: 
            height = SINGLE_HEIGHT
            wide = True
        elif size == QUART: 
            height = DOUBLE_HEIGHT
            wide = True
        elif size == BIG: 
            height = self.TRIPLE_HEIGHT
            wide = True
        elif size == HALF: 
            height = self.FULL_HEIGHT
            wide = True
        else:
            valid_sizes = [
                SINGLE,
                WIDE,
                DOUBLE,
                QUART,
                TRIPLE,
                BIG,
                FULL,
                HALF
            ]
            raise TypeError("size: " + ",".join(valid_sizes))

        if wide: 
            width = DOUBLE_WIDTH
            limit = 100
        lines_per_entry = 1 + info_lines
        inner_height = height - 2*padding - info_line
        line_count = int(inner_height / MINLINE_HEIGHT)
        while line_count % lines_per_entry != 0:
            line_count -= 1
        line_height = 1.0 * inner_height / line_count

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(x, y-height, width, height, o_rad, stroke, 1)
        self.drawTitle(canvas, x, y, height, title)

        # this creates the appropriate header bar
        info_y = y - padding - info_line
        info_x = x + bar
        xp_width = 25
        desc_width = width - bar - xp_width
        canvas.roundRect(
            info_x,
            info_y,
            desc_width,
            info_line,
            i_rad,
            stroke,
            1
        )
        canvas.roundRect(
            info_x + desc_width,
            info_y,
            xp_width,
            info_line,
            i_rad,
            stroke,
            1
        )

        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont(FONT_NAME, 7)

        offset = 2
        canvas.drawString(
            info_x + 4,
            info_y+offset,
            msg.PDF_NAME_AND_INFO
        )
        canvas.drawCentredString(
            info_x + desc_width + xp_width/2,
            info_y + offset,
            msg.XP
        )

        # filter traits ... based on trait_type
        traits = self.char.getTraits()
        trait_list = []
        if trait_type == "all":
            trait_list = traits
        else:
            for trait in traits:
                xp = int(trait.get("xp","0"))
                if xp >= 0 and trait_type == "positive":
                    trait_list.append(trait)
                elif xp < 0 and trait_type == "negative":
                    trait_list.append(trait)
                
        # draw the lines (and fill in skills if they exist ...                     
        trait_count = start_index

        canvas.setFont(FONT_NAME, 10)
        offset = 3

        i = line_count - 1
        while i >= 0:
            # construct the line ... 
            local_y = (y + padding - height) + line_height * i
            local_x = (x + bar)

            i -= lines_per_entry

            # boxes
            canvas.setFillColorRGB(1, 1, 1)
            # name_box
            canvas.roundRect(
                local_x,
                local_y,
                desc_width,
                line_height,
                i_rad,
                stroke,
                1
            )
            # xp_box
            local_x += desc_width
            canvas.roundRect(
                local_x,
                local_y,
                xp_width,
                line_height,
                i_rad,
                stroke,
                1
            )
            # info_box
            if info_lines > 0: 
                box_height = info_lines * line_height
                temp_y = local_y - box_height
                local_x = x + bar
                canvas.roundRect(
                    local_x,
                    temp_y,
                    width - bar,
                    box_height,
                    i_rad,
                    stroke,
                    1
                )

            # is there a trait to fill in?
            if trait_count < len(trait_list):
                trait = trait_list[trait_count]
                trait_xp = trait.get("xp", "0")
                trait_name = trait.get("name", "")
                trait_spec = ""
                trait_vars = []
                trait_rank = ""

                full_trait = self.traits.getTrait(trait_name)
                
                selected = trait.find("selected")
                if (full_trait is not None) and (selected is not None): 
                    # add specification
                    spec = selected.get("spec", "")
                    if spec:
                        trait_spec = "("+spec+")"
                    
                    # add rank    
                    full_ranks = full_trait.findall("rank")
                    if full_ranks:
                        rank_id = "rank-"+full_ranks[0].get("id")
                        rank = selected.get(rank_id, "")
                        if rank:
                            trait_rank = "["+rank+"]"

                    # description (base)
                    description = [
                        trait.find("description"),
                        full_trait.find("description")
                    ]

                    # variables
                    full_variables = full_trait.findall("variable")
                    for variable in full_variables:
                        var_id = "id-"+variable.get("id", "")
                        var_name = variable.get("name", "")
                        if var_name:
                            value = selected.get(var_id, "")
                            trait_vars.append((var_name, value))
                            search = "description[@value='"+value+"']"
                            description.append(variable.find(search))
                
                canvas.setFillColorRGB(0, 0, 0)
                local_x = x + bar

                for desc in description:
                    if desc is None:
                        description.remove(desc)
                
                # add specification and rank to name ... 
                trait_name += " " + trait_spec + trait_rank

                # add variables (for one liners ...)
                if info_lines == 0:
                    v_count = 0
                    while v_count < len(trait_vars):
                        if v_count == 0:
                            trait_name += "("
                        trait_name += trait_vars[v_count][1]
                        v_count += 1
                        if v_count < len(trait_vars):
                            trait_name += ","
                        else:
                            trait_name += ")"

                # and trim ...                
                if len(trait_name) > limit:
                    trait_name = trait_name[0:limit] + "..."
                canvas.drawString(
                    local_x + offset,
                    local_y + offset,
                    trait_name
                )

                # xp
                canvas.drawCentredString(
                    local_x + desc_width + xp_width/2,
                    local_y + offset,
                    trait_xp
                )

                # fill the info box ...
                if info_lines > 0: 
                    local_x = x + bar
                    info_limit = limit + 10
                    cur_line = 0

                    text = ""

                    v_count = 0
                    while v_count < len(trait_vars) and cur_line < info_lines:
                        var_text = "{name}: {value}".format(
                            name=trait_vars[v_count][0],
                            value=trait_vars[v_count][1]
                        )
                        if len(text) + len(var_text) > info_limit: 
                            local_y -= line_height
                            cur_line += 1
                            canvas.drawString(
                                local_x + offset,
                                local_y + offset,
                                text
                            )
                            text = var_text
                        else:
                            text += var_text
                        v_count += 1
                        if v_count < len(trait_vars):
                            text += ", "
                    # add final line of variables text ... 
                    if text != "":
                        local_y -= line_height
                        cur_line += 1
                        canvas.drawString(
                            local_x + offset,
                            local_y + offset,
                            text
                        )
                        text = ""

                    # add description to the lines that are still remaining ... 
                    desc_count = 0
                    while cur_line < info_lines:
                        if desc_count < len(description):
                            desc_element = description[desc_count]
                            desc_words = desc_element.text.split()

                            # render text for one description ... 
                            word_count = 0
                            while word_count < len(desc_words):
                                l = len(text) + len(desc_words[word_count])
                                if l < info_limit:
                                    text += " "+desc_words[word_count]
                                    word_count += 1
                                else: 
                                    local_y -= line_height
                                    cur_line += 1
                                    if (cur_line == info_lines
                                        and word_count < len(desc_words)
                                    ):
                                        text += "..."
                                    canvas.drawString(
                                        local_x + offset,
                                        local_y + offset,
                                        text
                                    )
                                    text = ""
                                    if cur_line == info_lines:
                                        break
                            # the final line ... 
                            if text != "":
                                local_y -= line_height
                                cur_line += 1
                                canvas.drawString(
                                    local_x + offset,
                                    local_y + offset,
                                    text
                                )
                                text = ""

                            desc_count += 1
                        cur_line += 1
            trait_count += 1

    def moduleSkills(
        self,
        canvas,
        x,
        y,
        size=SINGLE,
        skill_type="all",
        start_index=0
    ):
        """ this module draws a box with the characters skills
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "single", "double", "triple", "full"
        skill_type: string - "all", "active", "passive", "knowledge", "lang"
        start_index: int - where to start in the skill list ...
        """

        # localize variables for easy use ... 
        limit = 30
        info_line = INFO_LINE
        width = SINGLE_WIDTH
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING

        # type cleanup ...
        start_index = int(start_index)

        stroke = STROKE
        bar = BAR_WIDTH

        # set the title based on the selected skill_type
        if skill_type == "all":
            title = msg.PDF_SKILLS.upper()
        elif skill_type == "active":
            title = msg.PDF_SKILLS_ACTIVE.upper()
        elif skill_type == "passive":
            title = msg.PDF_SKILLS_PASSIVE.upper()
        elif skill_type == "knowledge":
            title = msg.PDF_SKILLS_KNOWLEDGE.upper()
        elif skill_type == "lang":
            title = msg.PDF_SKILLS_LANGUAGE.upper()
        else:

            raise TypeError("Invalid skill_type")

        # handle different sizes

        wide = False
        # handle different sizes
        if size == SINGLE: 
            height = SINGLE_HEIGHT
        elif size == DOUBLE: 
            height = DOUBLE_HEIGHT
        elif size == TRIPLE: 
            height = TRIPLE_HEIGHT
        elif size == FULL: 
            height = FULL_HEIGHT
        elif size == WIDE: 
            height = SINGLE_HEIGHT
            wide = True
        elif size == QUART: 
            height = DOUBLE_HEIGHT
            wide = True
        elif size == BIG: 
            height = TRIPLE_HEIGHT
            wide = True
        elif size == HALF: 
            height = FULL_HEIGHT
            wide = True
        else: 
            valid_sizes = [
                SINGLE,
                WIDE,
                DOUBLE,
                QUART,
                TRIPLE,
                BIG,
                FULL,
                HALF
            ]
            raise TypeError("size: " + ",".join(valid_sizes))

        if wide: 
            width = DOUBLE_WIDTH
            limit = 70
        inner_height = height - 2*padding - info_line
        line_count = int(inner_height / MINLINE_HEIGHT)
        line_height = 1.0 * inner_height / line_count

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(
            x,
            y-height,
            width,
            height,
            o_rad,
            stroke,
            1
        )
        
        self.drawTitle(canvas, x, y, height, title)

        # create the columns: 
        spec_col = 12
        skill_col = 8
        desc_col = width - bar - spec_col - 3 * skill_col

        # this creates the appropriate header bar
        info_y = y - padding - info_line
        info_x = x + bar
        canvas.roundRect(
            info_x,
            info_y,
            spec_col,
            info_line,
            i_rad,
            stroke,
            1
        )
        canvas.roundRect(
            info_x + spec_col,
            info_y,
            skill_col,
            info_line,
            i_rad,
            stroke,
            1
        )
        canvas.roundRect(
            info_x + spec_col + 1*skill_col,
            info_y,
            skill_col,
            info_line,
            i_rad,
            stroke,
            1
        )
        canvas.roundRect(
            info_x + spec_col + 2*skill_col,
            info_y,
            skill_col,
            info_line,
            i_rad,
            stroke,
            1
        )
        canvas.roundRect(
            info_x + spec_col + 3*skill_col,
            info_y,
            desc_col,
            info_line,
            i_rad,
            stroke,
            1
        )

        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont(FONT_NAME, 7)

        offset = 2
        canvas.drawCentredString(
            info_x + 0.5*spec_col,
            info_y + offset,
            "S"
        )
        canvas.drawCentredString(
            info_x + spec_col + 0.5*skill_col,
            info_y + offset,
            "1"
        )
        canvas.drawCentredString(
            info_x + spec_col + 1.5*skill_col,
            info_y + offset,
            "2"
        )
        canvas.drawCentredString(
            info_x + spec_col + 2.5*skill_col,
            info_y + offset,
            "3"
        )
        canvas.drawString(
            info_x + spec_col + 3*skill_col + 3,
            info_y + offset,
            msg.PDF_SKILLNAME
        )

        # filter skills ... based on skill_type
        skills = self.char.getSkills()
        skill_list = []
        if skill_type == "all":
            skill_list = skills
        else:
            if skill_type == "knowledge":
                skill_type = "passive"
            elif skill_type == "passive":
                skill_type = ["passive", "lang"]

            for skill in skills:
                if skill.get("type") in skill_type:
                    skill_list.append(skill)

        # draw the lines (and fill in skills if they exist ...                     
        skill_count = start_index
        i = line_count - 1
        canvas.setFont(FONT_NAME, 10)

        while i >= 0:
            line_y = (y + 2 - height) + line_height * i
            line_x = (x + bar)
            
            # retrieve the skill data ...
            skill_spec = ""
            skill_name = ""
            skill_value = 0            
            if skill_count < len(skill_list):
                skill = skill_list[skill_count]
                skill_value = int(skill.get("value", "0"))
                skill_name = skill.get("name", "")
                if len(skill_name) > limit:
                    skill_name = skill_name[0:limit] + "..."
                skill_spec_val = skill.get("spec", "1")
                if skill_spec_val == "1":
                    skill_spec = "G"
                if skill_spec_val == "2":
                    skill_spec = "F"
                if skill_spec_val == "3":
                    skill_spec = "S"

            # construct the line ... 
            canvas.setFillColorRGB(1, 1, 1)
            # spec box
            canvas.roundRect(
                line_x,
                line_y,
                spec_col,
                line_height,
                i_rad,
                stroke,
                1
            )
            # skill 1
            line_x += spec_col
            canvas.roundRect(
                line_x,
                line_y,
                skill_col,
                line_height,
                i_rad,
                stroke,
                1
            )
            if skill_value >= 1: 
                canvas.setFillColorRGB(0, 0, 0)
                canvas.roundRect(
                    line_x + 1,
                    line_y + 1,
                    skill_col - 2,
                    line_height - 2,
                    1,
                    0,
                    1
                )
            # skill 2
            line_x += skill_col
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(
                line_x,
                line_y,
                skill_col,
                line_height,
                i_rad,
                stroke,
                1
            )
            if skill_value >= 2: 
                canvas.setFillColorRGB(0, 0, 0)
                canvas.roundRect(
                    line_x + 1,
                    line_y + 1,
                    skill_col - 2,
                    line_height - 2,
                    1,
                    0,
                    1
                )
            # skill_3
            line_x += skill_col
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(
                line_x,
                line_y,
                skill_col,
                line_height,
                i_rad,
                stroke,
                1
            )
            if skill_value == 3: 
                canvas.setFillColorRGB(0, 0, 0)
                canvas.roundRect(
                    line_x + 1,
                    line_y + 1,
                    skill_col - 2,
                    line_height - 2,
                    1,
                    0,
                    1
                )
            # skill_name
            line_x += skill_col
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(
                line_x,
                line_y,
                desc_col,
                line_height,
                i_rad,
                stroke,
                1
            )
            canvas.setFillColorRGB(0, 0, 0)
            canvas.drawString(
                x+bar+4,
                line_y+3,
                skill_spec
            )
            canvas.drawString(
                line_x+4,
                line_y+3,
                skill_name
            )

            skill_count += 1
            i -= 1

    def moduleEquipment(
        self,
        canvas,
        x,
        y,
        size=SINGLE,
        item_id=-1,
        condensed=False,
        equipped=False,
        content=False,
        item_type=None,
        exclude=None,
        content_exclude=None,
        info_lines=0
    ):

        """ This module is used to render a wide range of inventory related elements on the character sheet
        for this reason please refer to the notes on which variables to combine ... 
            canvas: reportlab pdf canvas
            x,y: int - top left corner in points
            size: string - "single", "double", "triple", "full"
            item_id: int > 0 - this creates a specific bag or container inventory displaying all items packed into that item
            condensed: bool - condense items for display
            equipped: bool - only list equipped items 
            content: bool - list content of displayed items
            item_type: comma separated string => list
            exclude: comma separated string => list
            content_exclude: comma separated string => list
            info_lines: int - number of info lines ... 

            How to combine the variabls ...
            item_id - use it to display the contents of a single container
                        all other variables will be ignored!
            condensed - the list will condense identical items that are scattered
                        among different containers, like bullets in clips or chambers ...   
            equipped - the list will only contain equipped items
                        + content (show packed items inside those)
            item_type - limits selection to items of these types
            exclude - if you want to just exclude a few types from the "all" list ...         
            """

        # localize variables for easy use ... 
        width = SINGLE_WIDTH
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING
        
        limit = 48
        stroke = STROKE
        bar = BAR_WIDTH
        info_line = INFO_LINE
        spacer = 0

        # type cleanup ...
        info_lines = int(info_lines)
        item_id = int(item_id)

        if item_type:
            item_type = item_type.split(",")

        if exclude:
            exclude = exclude.split(",")
        else:
            exclude = []

        if content_exclude:
            content_exclude = content_exclude.split(",")
        else:
            content_exclude = []

        wide = False
        # handle different sizes
        if size == SINGLE: 
            height = SINGLE_HEIGHT
        elif size == DOUBLE: 
            height = DOUBLE_HEIGHT
        elif size == TRIPLE: 
            height = TRIPLE_HEIGHT
        elif size == FULL: 
            height = FULL_HEIGHT
        elif size == WIDE: 
            height = SINGLE_HEIGHT
            wide = True
        elif size == QUART: 
            height = DOUBLE_HEIGHT
            wide = True
        elif size == BIG: 
            height = TRIPLE_HEIGHT
            wide = True
        elif size == HALF: 
            height = FULL_HEIGHT
            wide = True
        else: 
            valid_sizes = [
                SINGLE,
                WIDE,
                DOUBLE,
                QUART,
                TRIPLE,
                BIG,
                FULL,
                HALF
            ]
            raise TypeError("size: " + ",".join(valid_sizes))

        if wide: 
            width = DOUBLE_WIDTH
            limit = 100

        inner_height = height - 2*padding - info_line
        line_count = int(inner_height / MINLINE_HEIGHT)
        lines_per_entry = 1 + info_lines
        while line_count % lines_per_entry != 0:
            line_count -= 1
        line_height = 1.0 * inner_height / line_count
        if lines_per_entry > 1:
            spacer = 1

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(x, y-height, width, height, o_rad, stroke, 1)

        # set title
        title = msg.PDF_EQUIPMENT.upper()
        # based on item ...
        if item_id >= 0:
            item = self.char.getItemById(str(item_id))
            if item is not None: 
                title = item.get("name").upper()
                container = item.find("container")
                if container is not None:
                    title = container.get("name").upper()
        # based on item_type
        elif item_type is not None:
            if it.CLOTHING in item_type:
                title = msg.PDF_CLOTHING_AND_MORE.upper()
            melee_weapons = [
                it.CLUBS,
                it.NATURAL,
                it.STAFFS,
                it.BLADES
            ]
            if any(melee_weapons, item_type) and len(item_type) > 1:
                title = msg.PDF_MELEE.upper()
            guns = [
                it.PISTOLS,
                it.REVOLVERS,
                it.RIFLES,
                it.RIFLES_SA,
                it.SHOT_GUNS,
                it.SHOT_GUNS_SA,
                it.AUTOMATIC_PISTOLS,
                it.MASCHINE_GUNS,
                it.AUTOMATIC_RIFLES,
                it.BLASTER
            ]
            if any(guns, item_type) and len(item_type) > 1:
                if title == msg.PDF_MELEE:
                    title = msg.PDF_WEAPONS.upper()
                else:
                    title = msg.PDF_GUNS.upper()

        self.drawTitle(canvas, x, y, height, title)

        # construct the appropriate itemlist ...
        item_list = []
        # for item_id ... 
        if item_id >= 0: 
            item = self.char.getItemById(item_id)
            if item is not None: 
                item_ids = item.get("content", "")
                item_ids = item_ids.split()
                for id in item_ids:
                    sub_item = self.char.getItemById(str(id))
                    if sub_item is not None:
                        item_list.append(sub_item)
        else:
            # get the full list ... 
            items = self.char.getItems()
            
            # create the condensed list ... 
            if condensed:
                for item in items:
                    name = item.get("name")
                    i_type = item.get("type")
                    
                    valid_item = False
                    # check item_type ... 
                    if item_type is None:
                        valid_item = True
                    elif i_type in item_type:
                        valid_item = True
                    # check exclude
                    if valid_item and i_type in exclude:
                        valid_item = False
                    
                    if valid_item: 
                        item_added = False
                        for some_item in item_list:
                            some_name = some_item.get("name")
                    
                            # check for name
                            if some_name == name:
                                # retrieve additional information
                                options = item.findall("option")
                                some_options = some_item.findall("option")
                                identical = True
                                # further comparison
                                for option in options: 
                                    option_name = option.get("name")
                                    option_value = option.get("value")
                                    for some_option in some_options:
                                        s_option_name = some_option.get("name")
                                        s_option_value = some_option.get("value")
                                        if (option_name == s_option_name
                                            and option_value != s_option_value
                                        ):
                                            identical = False
                                            break
                                    if not identical:
                                        break
                                if identical: 
                                    quantity = int(item.get("quantity"))
                                    some_quantity = int(some_item.get("quantity"))
                                    some_item.set(
                                        "quantity",
                                        str(quantity+some_quantity)
                                    )
                                    item_added = True
                        # ... or add the item to the list ... 
                        if item_added is False:
                            item_list.append(item)

            else: 
                # list of unequipped items ... 
                if equipped is False:
                    for item in items: 
                        # check for item_list and exclude ... 
                        if item_type is None and item.get("type") not in exclude:
                            item_list.append(item)
                        if item_type is not None: 
                            if item.get("type") in item_type:
                                item_list.append(item)
                
                # equipped items, show no contents ... 
                elif equipped is True and content is False:
                    for item in items: 
                        if item.get("equipped", "0") == "1":
                            # check for item_list and exclude ... 
                            if (item_type is None
                                and item.get("type") not in exclude
                            ):
                                item_list.append(item)
                            if item_type is not None: 
                                if item.get("type") in item_type:
                                    item_list.append(item)

                # equipped items, show their contents ... 
                elif equipped is True and content == True:
                    for item in items: 
                        if item.get("equipped", "0") == "1":
                            # check for item_list and exclude ... 
                            item_included = False
                            if (item_type is None
                                and item.get("type") not in exclude
                            ):
                                    item_list.append(item)
                                    item_included = True
                            if item_type is not None: 
                                if item.get("type") in item_type: 
                                    item_list.append(item)
                                    item_included = True

                            # add sub_items if the item is included in the list
                            # and the type not listed in the
                            # exclude_content list ...
                            
                            if (item_included
                                and item.get("type") not in content_exclude
                            ):
                                item_ids = item.get("content", "")
                                item_ids = item_ids.split()
                                for id in item_ids:
                                    sub_item = self.char.getItemById(str(id))
                                    if sub_item is not None:
                                        item_list.append(sub_item)

        # this creates the appropriate header bar
        info_y = y - padding - info_line
        info_x = x + bar
        quality_width = 0.75*line_height
        amount_width = 1.25*line_height
        weight_width = 2.0*line_height
        text_width = width - bar - 4.0 * line_height
        canvas.roundRect(
            info_x,
            info_y,
            quality_width,
            info_line,
            i_rad,
            stroke,
            1
        )
        info_x += quality_width
        canvas.roundRect(
            info_x,
            info_y,
            amount_width,
            info_line,
            i_rad,
            stroke,
            1
        )
        info_x += amount_width
        canvas.roundRect(
            info_x,
            info_y,
            text_width,
            info_line,
            i_rad,
            stroke,
            1
        )
        info_x += text_width
        canvas.roundRect(
            info_x,
            info_y,
            weight_width,
            info_line,
            i_rad,
            stroke,
            1
        )

        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont(FONT_NAME, 7)

        info_x = x + bar
        offset = 2
        canvas.drawCentredString(
            info_x + quality_width/2,
            info_y+offset,
            "Q"
        )
        info_x += quality_width
        canvas.drawCentredString(
            info_x + amount_width/2,
            info_y+offset,
            msg.PDF_QUANTITY
        )
        info_x += amount_width
        canvas.drawString(
            info_x + offset,
            info_y+offset,
            msg.PDF_ITEMNAME
        )
        info_x += text_width
        canvas.drawCentredString(
            info_x + weight_width / 2,
            info_y+offset,
            msg.PDF_WEIGHT
        )

        # draw the lines (and fill in skills if they exist ...                     
        canvas.setFont(FONT_NAME, 10)
        local_y = y - padding - info_line
        i = line_count - 1
        item_selector = 0
        while i >= 0:
            # generate the info box ...
            i -= lines_per_entry
            local_y -= line_height
            local_x = x + bar
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(
                local_x,
                local_y,
                quality_width,
                line_height - spacer,
                i_rad,
                stroke,
                1
            )
            local_x += quality_width
            canvas.roundRect(
                local_x,
                local_y,
                amount_width,
                line_height - spacer,
                i_rad,
                stroke,
                1
            )
            local_x += amount_width
            canvas.roundRect(
                local_x,
                local_y,
                text_width,
                line_height - spacer,
                i_rad,
                stroke,
                1
            )
            local_x += text_width
            canvas.roundRect(
                local_x,
                local_y,
                weight_width,
                line_height - spacer,
                i_rad,
                stroke,
                1
            )
            local_x = x + bar
            if info_lines > 0: 
                box_height = info_lines * line_height
                temp_y = local_y - box_height
                if i < 0:
                    spacer = 0
                canvas.roundRect(
                    local_x,
                    temp_y + spacer,
                    width - bar,
                    box_height - spacer,
                    i_rad,
                    stroke,
                    1
                )

            # add item to info-box ...
            if item_selector < len(item_list):
                item = item_list[item_selector]
                item_name = item.get("name", "")
                item_quality = item.get("quality", "6")
                item_quantity = item.get("quantity", "1")
                item_weight = item.get("weight", "-")

                # line 1
                canvas.setFillColorRGB(0, 0, 0)
                local_x = x + bar
                canvas.drawCentredString(
                    local_x + quality_width/2.0,
                    local_y + 3,
                    item_quality
                )
                local_x += quality_width
                canvas.drawRightString(
                    local_x + amount_width - 3,
                    local_y + 3,
                    item_quantity
                )
                local_x += amount_width
                canvas.drawString(
                    local_x + 3,
                    local_y + 3,
                    item_name
                )
                local_x += text_width
                canvas.drawRightString(
                    local_x + weight_width - 3,
                    local_y + 3,
                    item_weight
                )

                # info lines : 
                if info_lines > 0: 
                    cur_line = 0
                    local_x = x + bar

                    # print selected options ... 
                    options = item.findall("option")
                    text = ""
                    text_2 = ""
                    for option in options: 
                        o_name = option.get("name")
                        o_value = option.get("value")
                        text += o_name + ": " + o_value + "  "
                        text_2 += "[" + o_value + "]"
                    
                    # shorten text if necessary
                    text = text.strip()
                    if len(text) > limit:
                        text = text_2
                    
                    # print text ... 
                    if len(text) > 0: 
                        cur_line += 1
                        local_y -= line_height
                        canvas.drawString(
                            local_x + 3,
                            local_y + 3,
                            text
                        )

                    # retrieve description
                    desc_words = []
                    description = item.find("description")
                    if description is not None:
                        if len(description.text) > 0:
                            desc_words = description.text.split()

                    word_count = 0
                    text = ""
                    while (word_count < len(desc_words)
                           and cur_line <= info_lines
                        ):
                        while len(text) + len(desc_words[word_count]) <= limit: 
                            text += desc_words[word_count] + " "
                            word_count += 1
                            if word_count == len(desc_words):
                                break
                        local_y -= line_height
                        cur_line += 1
                        if (cur_line == info_lines
                            and word_count < len(desc_words)
                        ):
                            text += " ..."
                        canvas.drawString(
                            local_x + 3,
                            local_y + 3,
                            text
                        )
                            
                        text = ""

                    # fill empty lines ... 
                    local_y -= (info_lines - cur_line) * line_height
            
            # ... or just move the cursor down ...
            else: 
                local_y -= info_lines * line_height

            # next item ... 
            item_selector += 1

    def moduleWeapons(
        self,
        canvas,
        x,
        y,
        size=SINGLE,
        equipped=False,
        variant=None,
        item_type=None,
        amount=False,
        info_lines=0
    ):
        """ This module is used to render a wide range of inventory related elements on the character sheet
            for this reason please refer to the notes on which variables to combine ... 
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "single", "double", "triple", "full"
        equipped: bool - only list equipped items 
        variant: string - "melee", "guns", "ammo"
        item_type: list [string,string,...] 
        amount: bool - show quantity if True
        info_lines: int - number of additional info lines ... 
        """

        # localize variables for easy use ... 
        width = SINGLE_WIDTH
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING

        limit = 40
        stroke = STROKE
        bar = BAR_WIDTH
        info_line = INFO_LINE

        # type cleanup ...
        info_lines = int(info_lines)

        spacer = 0

        wide = False
        # handle different sizes
        if size == SINGLE: 
            height = SINGLE_HEIGHT
        elif size == DOUBLE: 
            height = DOUBLE_HEIGHT
        elif size == TRIPLE: 
            height = TRIPLE_HEIGHT
        elif size == FULL: 
            height = FULL_HEIGHT
        elif size == WIDE: 
            height = SINGLE_HEIGHT
            wide = True
        elif size == QUART: 
            height = DOUBLE_HEIGHT
            wide = True
        elif size == BIG: 
            height = TRIPLE_HEIGHT
            wide = True
        elif size == HALF: 
            height = FULL_HEIGHT
            wide = True
        else: 
            valid_sizes = [
                SINGLE,
                WIDE,
                DOUBLE,
                QUART,
                TRIPLE,
                BIG,
                FULL,
                HALF
            ]
            raise TypeError("size: " + ",".join(valid_sizes))

        if wide: 
            width = DOUBLE_WIDTH
            limit = 100

        inner_height = height - 2*padding - info_line
        line_count = int(inner_height / MINLINE_HEIGHT)
        lines_per_entry = 1 + info_lines
        
        while line_count % lines_per_entry != 0:
            line_count -= 1
        line_height = 1.0 * inner_height / line_count

        if lines_per_entry > 1:
            spacer = 1

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(x, y-height, width, height, o_rad, stroke, 1)

        # set title
        title = msg.PDF_WEAPONS.upper()
        # based on variant ...
        if variant is not None:
            if variant == "melee": 
                title = msg.PDF_MELEE.upper()
                item_type = [
                    it.CLUBS,
                    it.NATURAL,
                    it.STAFFS,
                    it.BLADES,
                    it.OTHER_MELEE,
                    it.TOOLS
                ]
            elif variant == "guns": 
                title = msg.PDF_GUNS.upper()
                item_type = [
                    it.PISTOLS,
                    it.REVOLVERS,
                    it.RIFLES,
                    it.RIFLES_SA,
                    it.SHOT_GUNS,
                    it.SHOT_GUNS_SA,
                    it.AUTOMATIC_PISTOLS,
                    it.MASCHINE_GUNS,
                    it.AUTOMATIC_RIFLES,
                    it.BLASTER
                ]
            elif variant == "ammo": 
                title = msg.PDF_AMMO
                item_type = [it.AMMO]

        self.drawTitle(canvas, x, y, height, title)

        # construct the appropriate itemlist ...
        item_list = []
        items = self.char.getItems()
        if not equipped:
            for item in items: 
                # check for item_type 
                if item_type is None: 
                    if item.find("damage") is not None:
                        if item.get("type") != it.AMMO:
                            item_list.append(item)
                else: 
                    if item.get("type") in item_type: 
                        if item.find("damage") is not None:
                            item_list.append(item)
        else:                
            for item in items: 
                if item.get("equipped", "0") == "1":
                    # check for item_list and exclude ... 
                    if item_type is None: 
                        if item.find("damage") is not None:
                            if item.get("type") != it.AMMO:
                                item_list.append(item)
                    else:    
                        if item.get("type") in item_type: 
                            if item.find("damage") is not None:
                                item_list.append(item)

        # condense item_list ammo ... 
        if variant == "ammo":
            new_list = []
            for item in item_list:
                name = item.get("name")
                cal = "0"
                col = "0"
                cal_tag = item.find("option[@name='"+it.OPTION_CALIBER+"']")
                if cal_tag is not None:
                    cal = cal_tag.get("value", "0")
                col_tag = item.find("option[@name='"+it.OPTION_COLOR+"']")
                if col_tag is not None:
                    col = col_tag.get("value", "0")
                item_added = False
                for new_item in new_list:
                    new_name = new_item.get("name")
                    
                    # check for name
                    if new_name == name:
                        # retrieve additional information
                        new_cal = "0"
                        new_col = "0"
                        search = "option[@name='"+it.OPTION_CALIBER+"']"
                        new_cal_tag = item.find(search)
                        if new_cal_tag is not None:
                            new_cal = cal_tag.get("value", "0")
                        search = "option[@name='"+it.OPTION_COLOR+"']"
                        new_col_tag = item.find(search)
                        if new_col_tag is not None:
                            new_col = col_tag.get("value", "0")
                        # compare caliber and color and adjust quantity
                        if new_cal == cal and new_col == col:
                            quantity = int(item.get("quantity"))
                            new_quantity = int(new_item.get("quantity"))
                            new_item.set("quantity", str(quantity+new_quantity))
                            item_added = True
                # ... or add the item to the list ... 
                if not item_added:
                    new_list.append(item)
            # return the filtered item list ... 
            item_list = new_list

        # this renders the appropriate header bar
        info_y = y - padding - info_line
        info_x = x + bar
        quantity_width = 0
        if amount:
            quantity_width = 1.5 * line_height
        damage_width = 2.0*line_height
        name_width = width - bar - damage_width - quantity_width

        # limit characters per line... 
        info_limit = limit + 8
        if quantity_width > 0:
            limit -= 8
        
        if amount: 
            canvas.roundRect(
                info_x,
                info_y,
                quantity_width,
                info_line,
                i_rad,
                stroke,
                1
            )
            info_x += quantity_width
        canvas.roundRect(
            info_x,
            info_y,
            name_width,
            info_line,
            i_rad,
            stroke,
            1
        )
        info_x += name_width
        canvas.roundRect(
            info_x,
            info_y,
            damage_width,
            info_line,
            i_rad,
            stroke,
            1
        )
        canvas.setFillColorRGB(0, 0, 0)
        canvas.setFont(FONT_NAME, 7)
        info_x = x + bar
        offset = 2
        if amount:
            canvas.drawCentredString(
                info_x + quantity_width/2,
                info_y+offset,
                msg.PDF_QUANTITY
            )
            info_x += quantity_width
        canvas.drawString(
            info_x + offset,
            info_y+offset,
            msg.PDF_ITEMNAME
        )
        info_x += name_width
        canvas.drawCentredString(
            info_x + damage_width/2,
            info_y+offset,
            msg.PDF_DAMAGE
        )

        # draw the lines (and fill in skills if they exist ...                     
        canvas.setFont(FONT_NAME, 10)

        offset = 3
        local_y = y - padding - info_line
        i = line_count - 1
        item_selector = 0
        while i >= 0:
            i -= lines_per_entry
            # render the boxes ... 
            # for line 1 ... 
            local_y -= line_height
            local_x = x + bar
            canvas.setFillColorRGB(1, 1, 1)
            if amount:
                canvas.roundRect(
                    local_x,
                    local_y,
                    quantity_width,
                    line_height - spacer,
                    i_rad,
                    stroke,
                    1
                )
                local_x += quantity_width
            canvas.roundRect(
                local_x,
                local_y,
                name_width,
                line_height - spacer,
                i_rad,
                stroke,
                1
            )
            local_x += name_width
            canvas.roundRect(
                local_x,
                local_y,
                damage_width,
                line_height - spacer,
                i_rad,
                stroke,
                1
            )
            # and info lines info lines ...
            if lines_per_entry > 1:

                if i <= 0:
                    spacer = 0
                local_x = x+bar
                box_height = info_lines * line_height
                temp_y = local_y - box_height
                canvas.roundRect(
                    local_x,
                    temp_y + spacer,
                    width - bar,
                    box_height - spacer,
                    i_rad,
                    stroke,
                    1
                )

            # check if there is an item in the inventory to write to that line
            if item_selector < len(item_list):
                
                # get the data ...
                item = item_list[item_selector]
                # name
                item_name = item.get("name", "")
                # damage
                damage_tag = item.find("damage")
                item_damage = "0/0"
                if damage_tag is not None:
                    item_damage = damage_tag.get("value")
                # ammo tag
                ammo_tag = item.find("ammo")
                if ammo_tag is not None:
                    active_chamber = self.char.getActiveChamber(item)
                    loaded_ammo = ammo_tag.get("loaded", "-1")
                    ammo_list = loaded_ammo.split()
                    chambered_id = ammo_list[active_chamber - 1]
                    chambered_item = self.char.getItemById(chambered_id)
                    if chambered_item is not None: 
                        chambered_damage = chambered_item.find("damage")
                        if chambered_damage is not None: 
                            item_damage = chambered_damage.get("value")
                # #caliber
                caliber = None
                caliber_tag = item.find("option[@name='"+it.OPTION_CALIBER+"']")
                if caliber_tag is not None:
                    caliber = caliber_tag.get("value")
                
                # cleanup the damage text ...
                damage_data = item_damage.split("/")
                s = 0
                d = 0
                e = ""
                if len(damage_data) >= 2: 
                    s = int(damage_data[0])
                    d = int(damage_data[1])
                if len(damage_data) == 3:
                    e = damage_data[2]
                s = str(s)
                if d > 0:
                    d = "+"+str(d)
                else:
                    d = str(d)
                if e != "":
                    e = "("+e+")"
                item_damage = s + "/" + d + e

                # adding text to line 1
                canvas.setFillColorRGB(0, 0, 0)
                local_x = x + bar
                if amount:
                    item_quantity = item.get("quantity")
                    canvas.drawRightString(
                        local_x + quantity_width - offset,
                        local_y + offset,
                        item_quantity
                    )
                    local_x += quantity_width

                if lines_per_entry == 1 and caliber:
                    item_name += " ["+caliber+"]"
                if len(item_name) > limit:
                    item_name = item_name[0:limit]+"..."
                canvas.drawString(
                    local_x + offset,
                    local_y + offset,
                    item_name
                )
                
                local_x += name_width
                canvas.drawCentredString(
                    local_x + damage_width/2,
                    local_y + offset,
                    item_damage
                )

                # adding stuff to the info lines ... 
                if info_lines > 0:
                    # capacity ... 
                    capacity_text = ""
                    if ammo_tag is not None: 
                        number_chambers = int(ammo_tag.get("chambers", "1"))
                        if number_chambers > 1: 
                            if info_lines == 1:
                                capacity_text = str(number_chambers)
                            else:
                                capacity_text = "{num} {txt}".format(
                                    num=str(number_chambers),
                                    txt=msg.PDF_CHAMBERS
                                )
                        else: 
                            content_ids = item.get("content", "-1").split()
                            for id in content_ids: 
                                sub_item = self.char.getItemById(id)
                                if sub_item is not None:
                                    sub_type = sub_item.get("type")
                                    if sub_type == "Clip":
                                        sub_container = sub_item.find("container")
                                        if sub_container is not None:
                                            if info_lines == 1:
                                                capacity_text = sub_container.get("size","0")
                                            else:
                                                capacity_text = sub_container.get("size","0") + msg.PDF_CLIPSIZE
                    # caliber ... 
                    caliber_text = ""
                    if caliber is not None:
                        if info_lines == 1:
                            caliber_text = caliber
                        else:
                            caliber_text = msg.PDF_CALIBER + ": " + caliber
                    
                    # loaded round ... 
                    bullet_name = ""
                    if chambered_item is not None: 
                        bullet_name = chambered_item.get("name")
                        
                    if info_lines == 1:
                        text_1 = "["+caliber_text+"] : " + msg.MULTIPLY + capacity_text + " - " + bullet_name
                        if len(text_1)>info_limit : text_1 = text_1[0:info_limit]
                        text_2 = ""
                    else: 
                        text_1 = caliber_text + " - " + capacity_text
                        text_2 = ""
                        if len(bullet_name) > 1: text_2 = msg.PDF_AMMO + ": "+ bullet_name

                    desc_text = []
                    word_count = 0
                    description = item.find("description")
                    if description is not None: 
                        text = description.text
                        if text is not None:
                            desc_text = text.split()
                    cur_line = 0


                    canvas.setFillColorRGB(0, 0, 0)
                    while cur_line < info_lines: 
                        cur_line += 1
                        local_y -= line_height
                        text = ""
                        core_lines = False
                        if len(text_1) > 1 and cur_line == 1: 
                            text = text_1
                            core_lines = True
                        if len(text_2) > 1 and cur_line == 2: 
                            text = text_2
                            core_lines = True
                            
                        if not core_lines:
                            while len(text) < info_limit and word_count < len(desc_text):
                                next_word = desc_text[word_count]
                                if len(next_word) + len(text) < info_limit:
                                    if text == "": text = next_word
                                    else: text += " " + next_word
                                    word_count += 1
                                else: break
                            if word_count < len(desc_text) and cur_line == info_lines: text += "..."
                        local_x = x + bar
                        canvas.drawString(local_x+offset,local_y+offset,text)
            else:
                local_y -= info_lines*line_height
            
            # #next entry .. 
            item_selector += 1

    # ##############END OF WEAPONS BOX # ###############




    # ##############DRAW A CONTACTS BOX # ###############

    def moduleContacts(self,canvas,x,y,size = SINGLE, contact_type = "all", extended = True, info_lines = 2):
        """ this module draws a box with contacts
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "single", "double", "triple", "full"
        contact_type: string - "all", "friends", "enemies"
        extended: bool - show description (only for size > "single")
        desc_lines: int - how many lines to show ... 
        """

        # localize variables for easy use ... 
        width = SINGLE_WIDTH
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING

        stroke = STROKE
        bar = BAR_WIDTH
        info_line = INFO_LINE

        # type cleanup ...
        info_lines = int(info_lines)


        # handle trait_type
        if contact_type == "all": title = msg.PDF_CONTACTS.upper()
        elif contact_type == "friends": title = msg.PDF_FRIENDS.upper()
        elif contact_type == "enemies": title = msg.PDF_ENEMIES.upper()
        else: raise TypeError("contact_type: string - 'all', 'friends', 'enemies'")


        wide = False
        # handle different sizes

        # handle different sizes
        if size == SINGLE: 
            height = SINGLE_HEIGHT
            extended = False
            info_lines = 0
        elif size == DOUBLE: 
            height = DOUBLE_HEIGHT
        elif size == TRIPLE: 
            height = TRIPLE_HEIGHT
        elif size == FULL: 
            height = FULL_HEIGHT
        elif size == WIDE: 
            height = SINGLE_HEIGHT
            wide = True
            extended = False
            info_lines = 0
        elif size == QUART: 
            height = DOUBLE_HEIGHT
            wide = True
        elif size == BIG: 
            height = TRIPLE_HEIGHT
            wide = True
        elif size == HALF: 
            height = FULL_HEIGHT
            wide = True
        else: 
            valid_sizes = [SINGLE,WIDE,DOUBLE,QUART,TRIPLE,BIG,FULL,HALF]
            raise TypeError("size: " + ",".join(valid_sizes))


        if wide: 
           width = DOUBLE_WIDTH 
           limit = 100



        inner_height = height - 2*padding - 2*info_line
        line_count = int(inner_height / MINLINE_HEIGHT)
        while line_count%(info_lines+2) != 0: line_count -= 1

        line_height = 1.0 * inner_height / line_count

        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(x,(y-height),width,height,o_rad,stroke,1)
        self.drawTitle(canvas,x,y,height,title)        

        # this creates the appropriate header bar
        info_y = y - padding - info_line
        info_x = x + bar
        line_width = width - bar
        name_width = 0.6 * line_width
        location_width = 0.4 * line_width
        competency_width = 0.5 * line_width
        competency_val_w = 0.5/3 * line_width
        loyality_width = 0.5/3 * line_width
        frequency_width = 0.5/3 * line_width 

        canvas.setFillColorRGB(1, 1, 1)
        canvas.roundRect(info_x,info_y,name_width,info_line,i_rad,stroke,1)
        info_x += name_width
        canvas.roundRect(info_x,info_y,location_width,info_line,i_rad,stroke,1)
        canvas.setFillColorRGB(0, 0, 0)
        info_x = x + bar
        canvas.setFont(FONT_NAME,7)

        offset = 2
        canvas.drawString(info_x + offset ,info_y+offset,"Name")
        info_x += name_width
        canvas.drawString(info_x + offset,info_y+offset,"Ort")
        
        info_y -= info_line
        info_x = x + bar
        canvas.setFillColorRGB(1, 1, 1)
        canvas.roundRect(info_x,info_y,competency_width,info_line,i_rad,stroke,1)
        info_x += competency_width
        canvas.roundRect(info_x,info_y,competency_val_w,info_line,i_rad,stroke,1)
        info_x += competency_val_w
        canvas.roundRect(info_x,info_y,frequency_width,info_line,i_rad,stroke,1)
        info_x += frequency_width
        canvas.roundRect(info_x,info_y,loyality_width,info_line,i_rad,stroke,1)
        
        canvas.setFillColorRGB(0, 0, 0)
        info_x = x + bar
        canvas.drawString(info_x + offset ,info_y+offset,msg.PDF_COMPENTECY)
        info_x += competency_width
        canvas.drawCentredString(info_x + competency_val_w/2,info_y+offset,msg.PDF_COMP_LEVEL)
        info_x += competency_val_w
        canvas.drawCentredString(info_x + frequency_width/2 ,info_y+offset,msg.PDF_FREQUENCY)
        info_x += frequency_width
        canvas.drawCentredString(info_x + loyality_width/2,info_y+offset,msg.PDF_LOYALITY)


                
        # draw the lines (and fill in skills if they exist ...                     
 
        canvas.setFont(FONT_NAME,10)
        
        contacts = self.char.getContacts()
        
        # filter contact based on contact_type
        contact_list = []
        if contact_type == "all": contact_list = contacts
        else: 
            for contact in contacts:
                xp = int(contact.get("xp","0"))
                if xp >= 0 and contact_type == "friends": contact_list.append(contact)
                elif xp < 0 and contact_type == "enemies": contact_list.append(contact)

        
        contact_index = 0
        
        local_y = y - padding - 2*info_line
        i = line_count - 1
        contact_selector_selector = 0
        while i >= 0:
            local_y -= line_height
            local_x = x + bar

            if contact_index < len(contact_list): contact = contact_list[contact_index]
            else: contact = None
            contact_index += 1

            canvas.setFillColorRGB(1, 1, 1)
            mod = 1
            canvas.roundRect(local_x,local_y,name_width,line_height-mod,i_rad,stroke,1)
            local_x += name_width
            canvas.roundRect(local_x,local_y,location_width,line_height-mod,i_rad,stroke,1)
            
            if contact is not None:
                name = contact.get("name","")
                location = contact.get("location","")
                canvas.setFillColorRGB(0, 0, 0)
                local_x = x + bar
                offset = 3
                canvas.drawString(local_x + offset ,local_y+offset,name)
                local_x += name_width
                canvas.drawString(local_x + offset,local_y+offset,location)
            
            # next line
            i -= 1
            if i < 0: break

            local_y -= line_height
            local_x = x + bar
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(local_x,local_y,competency_width,line_height,i_rad,stroke,1)
            local_x += competency_width
            canvas.roundRect(local_x,local_y,competency_val_w,line_height,i_rad,stroke,1)
            local_x += competency_val_w
            canvas.roundRect(local_x,local_y,frequency_width,line_height,i_rad,stroke,1)
            local_x += frequency_width
            canvas.roundRect(local_x,local_y,loyality_width,line_height,i_rad,stroke,1)

            if contact is not None:
                competency_type = contact.get("competency","")
                competency = contact.get("competencylevel","")
                loyality = contact.get("loyality","")
                frequency = contact.get("frequency","")
                freq_text = ""
                if frequency == "0.25": freq_text = msg.PDF_FREQ_0
                elif frequency == "0.5": freq_text = msg.PDF_FREQ_1
                elif frequency == "0.75": freq_text = msg.PDF_FREQ_2
                elif frequency == "1.0": freq_text = msg.PDF_FREQ_3
                elif frequency == "1.5": freq_text = msg.PDF_FREQ_4
                elif frequency == "2.0": freq_text = msg.PDF_FREQ_5

                canvas.setFillColorRGB(0, 0, 0)
                local_x = x + bar
                canvas.drawString(local_x + offset ,local_y+offset,competency_type)
                local_x += competency_width
                canvas.drawCentredString(local_x + competency_val_w/2,local_y+offset,competency)
                local_x += competency_val_w
                canvas.drawCentredString(local_x + frequency_width/2 ,local_y+offset,freq_text)
                local_x += frequency_width
                canvas.drawCentredString(local_x + loyality_width/2,local_y+offset,loyality)

            # next line
            i -= 1
            if i < 0: break


            # add additional desc_lines ...
            if extended:  

                lines = 0
                while lines < info_lines:
                    lines += 1
                    i -= 1
                    if i < 0: break
                if i == 0: 
                    lines += 1
                    i -= 1
                temp_y = local_y
                local_y -= line_height * lines
                
                local_x = x + bar
                canvas.setFillColorRGB(1, 1, 1)
                mod = 1
                if i <= 0: mod = 0 
                canvas.roundRect(local_x,local_y+mod,width - bar,line_height*lines-mod,i_rad,stroke,1)
            
                # add description to box ... 
                # wrap if necessary
                if contact is not None:
                    line_length = 50
                    canvas.setFillColorRGB(0, 0, 0)
                
                    description = contact.find("description")
                    text = None
                    if description is not None: 
                        text = description.text
                    if text == None: text = ""
                    words = text.split()
                    text_lines = []
                    line_content = ""

                    for word in words:
                        if line_content == "": line_content = word
                        else: 
                            if len(line_content) + len(word) < line_length:
                                line_content += " " + word
                            else: 
                                text_lines.append(line_content)
                                line_content = word
                    text_lines.append(line_content)
                    
                    count = min(lines,len(text_lines))

                    num = 0
                    while num < count:
                        line = text_lines[num]
                        temp_y -= line_height
                        temp_x = x + bar
                        num += 1
                        if i == count and len(text_lines) >= count: 
                            line += "..."
                        canvas.drawString(temp_x + offset, temp_y + offset, line)
            

    # ##############END OF CONTACTS BOX # ###############


    # ################DRAW AN EWT BOX  # #################

    def moduleEWT(self,canvas,x,y,size=SINGLE):
        """ this module draws a EWT BOX
        canvas: reportlab pdf canvas
        x,y: int - top left corner in points
        size: string - "single"
        """

        # localize variables for easy use ... 
        line = 11
        col = 11

        width = SINGLE_WIDTH
        height = SINGLE_HEIGHT
        o_rad = OUTER_RADIUS
        i_rad = INNER_RADIUS
        padding = Y_PADDING
        
        stroke = STROKE
        bar = BAR_WIDTH

        title = msg.PDF_EWT_TITLE.upper()

        if size != SINGLE:
            raise TypeError("size: " + SINGLE)


        # draw the outer box ... 
        canvas.setFillColorRGB(0, 0, 0)
        canvas.roundRect(x,(y-height),width,height,o_rad,stroke,1)
        
        self.drawTitle(canvas,x,y,height,title)

        # draw the lines (and fill in skills if they exist ...                     
        ewt = config.EWT
        
        ewt_20 = ImageReader("images/ewt_20.png")
        ewt_10 = ImageReader("images/ewt_10.png")
        ewt_05 = ImageReader("images/ewt_05.png")
        ewt_00 = ImageReader("images/ewt_00.png")

        roll_width = 10
        inner_width = width - bar
        
        box_dims = (inner_width - roll_width) / 15.0

        firstline_height = height - 2*padding - 10*box_dims
        canvas.setFont(FONT_NAME,firstline_height-5)

        # corner box
        local_x = x + bar
        local_y = y - padding - firstline_height
        canvas.roundRect(local_x,local_y,roll_width,firstline_height,i_rad,1,1)
        local_x += roll_width

        # first line
        for i in range(15):
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(local_x,local_y,box_dims,firstline_height,i_rad,1,1)
            canvas.setFillColorRGB(0, 0, 0)
            canvas.drawCentredString(local_x+(0.5*box_dims),local_y+3,str(i-7))
            local_x += box_dims
        
        # the ewt matrix
        for line_count in range(10):
            local_y -= box_dims 
            local_x = x + bar
            canvas.setFillColorRGB(1, 1, 1)
            canvas.roundRect(local_x,local_y,roll_width,box_dims,i_rad,stroke,1)
            canvas.setFontSize(box_dims-2)
            canvas.setFillColorRGB(0, 0, 0)
            text = str(line_count+1)[-1]
            canvas.drawCentredString(local_x+(0.5*roll_width),local_y+2,text)
            
                
            for column_count in range (15):
                local_x = x + bar + roll_width + box_dims * column_count
                canvas.setFillColorRGB(1, 1, 1)
                canvas.roundRect(local_x,local_y,box_dims,box_dims,i_rad,stroke,1)
                value = ewt[line_count][column_count]
                if value == 2.0: img = ewt_20
                if value == 1.0: img = ewt_10
                if value == 0.5: img = ewt_05
                if value == 0.0: img = ewt_00

                canvas.drawImage(img,local_x + 1, local_y + 1, width = 9, height = 9,mask = "auto")

    # load and crop an image to place it on the canvas ... 
    def _loadImage(self,size,width,height):
                # load the image ...
        image_tag = self.char.getImage()
        image = None
        if image_tag is not None:
            filename = image_tag.get("file")
            image = Image.open(filename)
        if image is not None:
            size_tag = image_tag.find("size[@name='"+size+"']")

            ratio = 1.0 * width / height
            image_width = image.size[0]
            image_height = image.size[1]
            image_ratio = 1.0 * image_width / image_height

            # get positioning data from xml ...
            if size_tag is not None: 
                x_start = float(size_tag.get("x"))
                y_start = float(size_tag.get("y"))
                scale = float(size_tag.get("scale"))

            # ... or try to place the image anyway ...
            else:
                scale = min(1.0, 1.0*ratio/image_ratio)
                if image_ratio > ratio:
                    x_start = 0.5 - 0.5 * ratio
                    y_start = 0
                else:
                    x_start = 0.0
                    y_start = 0.5 - 0.5 / ratio

            # crop image based on selection 
            x1 = int(x_start * image_width)
            y1 = int(y_start * image_height)
            crop_width = int(1.0 * image_width * scale)
            crop_height = int(1.0 * image_width / ratio * scale)
            x2 = x1 + crop_width
            y2 = y1 + crop_height
            cropped_image = image.crop((x1,y1,x2,y2))

            # overwrite
            image = cropped_image
        return image

