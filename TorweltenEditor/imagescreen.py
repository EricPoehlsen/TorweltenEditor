"""
This module contains the Class for the character image selection
"""


import tkinter as tk
import config
import tkinter.filedialog as tkfd
import exportpdf
import xml.etree.ElementTree as et
from PIL import ImageTk,Image,PngImagePlugin,JpegImagePlugin

msg = config.Messages()
page = config.Page()


class ImageScreen(tk.Frame):
    """ Create and Display a screen for selecting a character image and 
    fitting selections for different aspect ratios used in the PDF Export.
    """
    def __init__(self, main, app):
        tk.Frame.__init__(self, main)

        self.app = app
        self.char = app.char

        self.image = None
        self.images = []

        self.variants = {}
        self.selected_size = ""
        self.selected_ratio = 0

        self.x = None
        self.y = None

        # this checks if there are still operations going on ... 
        self.finished = 0
        self.update = 0

        # create canvas ... 
        self.edit_frame = tk.Frame(self)
        self.edit_frame.pack(side=tk.LEFT, fill=tk.X, expand=1, anchor=tk.N)

        self.image_canvas = tk.Canvas(self, width=540, height=540)
        self.image_canvas.bind("<B1-Motion>", self._moveFrame)
        self.image_canvas.bind("<ButtonRelease-1>", self._stopMotion)
        self.image_canvas.bind_all("+", self._scaleFrame)
        self.image_canvas.bind_all("-", self._scaleFrame)
        self.image_canvas.bind_all("<Left>", self._moveFrame)
        self.image_canvas.bind_all("<Right>", self._moveFrame)
        self.image_canvas.bind_all("<Up>", self._moveFrame)
        self.image_canvas.bind_all("<Down>", self._moveFrame)

        self.image_canvas.pack(side=tk.LEFT)

        self.load_button = tk.Button(self.edit_frame)
        self.load_button.pack()
        
        self._checkForImage()
        
        # TEST
        tk.Button(self.edit_frame, text="TESTEXPORT", command=self._test).pack()

        self.variant_frame = tk.LabelFrame(
            self.edit_frame,
            text=msg.IS_SET_SELECTION
        )
        
        self.img_on_canvas = None
        self.rect = None

        # try loading an existing image ...
        image_tag = self.char.getImage()
        if image_tag is not None:
            self.update_idletasks()
            filename = image_tag.get("file") 
            self.image = Image.open(filename)
            self._displayImage()
 
    # display the file open dialog and load an image 
    def loadImageWindow(self):
        options = {}
        options['defaultextension'] = '.jpg'
        options['filetypes'] = [(msg.IS_LOAD_MIME, ('.jpg', '.png'))]
        # options['initialdir'] = 'C:\\'
        # options['initialfile'] = 'character.xml'
        options['parent'] = self
        options['title'] = msg.IS_LOAD_IMAGE_TITLE
        filename = tkfd.askopenfilename(**options)
        if filename:
            try:
                self.image = Image.open(filename)
                self.char.setImage(filename)
                self._displayImage()
                self._checkForImage()
            except IOError:
                self.imageError(filename)
                pass
        else:
            pass

    # show an error when image file is not an image file ... 
    def imageError(self, filename):
        window = tk.Toplevel()
        window.title(msg.IS_ERROR)
        img = ImageTk.PhotoImage(file="img/exclamation.png")
        icon = tk.Label(window, image=img)
        icon.image = img
        icon.grid(row=0, column=0)
        message = tk.Text(window, width=40, wrap=tk.WORD, height=5)
        message.insert("0.0", msg.IS_ERROR_TEXT %(filename))
        message.config(
            font="Arial 10 bold",
            state=tk.DISABLED,
            background="#eeeeee"
        )
        message.grid(row=0, column=1)
        button = tk.Button(
            window,
            text=msg.IS_ERROR_CLOSE,
            command=window.destroy)
        button.grid(row=1, column=0, columnspan=2)

    def _displayImage(self):
        if self.image is not None:
            real_width = self.image.size[0]
            real_height = self.image.size[1]
            canvas_dim = self.image_canvas.winfo_reqheight()
            scale1 = 1.0 * canvas_dim / real_width
            scale2 = 1.0 * canvas_dim / real_height
            scale = min(scale1, scale2)
            size_x = max(int(real_width*scale), 1)
            size_y = max(int(real_height*scale), 1)

            resized = self.image.resize((size_x, size_y))
            tk_image = ImageTk.PhotoImage(image = resized)
            self.images.append(tk_image)
            self.img_on_canvas = self.image_canvas.create_image(
                int(canvas_dim/2),  # x
                int(canvas_dim/2),  # y
                image=tk_image
            )
            
            self._showAspectButtons()

    @staticmethod
    def _aspectRatios():
        aspect = {
            page.SINGLE: 1.0 * page.SINGLE_WIDTH/page.SINGLE_HEIGHT,
            page.WIDE: 1.0 * page.DOUBLE_WIDTH/page.SINGLE_HEIGHT,
            page.DOUBLE: 1.0 * page.SINGLE_WIDTH/page.DOUBLE_HEIGHT,
            page.QUART: 1.0 * page.DOUBLE_WIDTH/page.DOUBLE_HEIGHT,
            page.TRIPLE: 1.0 * page.SINGLE_WIDTH/page.TRIPLE_HEIGHT,
            page.BIG: 1.0 * page.DOUBLE_WIDTH/page.TRIPLE_HEIGHT,
            page.FULL: 1.0 * page.SINGLE_WIDTH/page.FULL_HEIGHT,
            page.HALF: 1.0 * page.DOUBLE_WIDTH/page.FULL_HEIGHT,
            page.ATTRIB_IMAGE: 0.805464  # every code needs magic numbers :P
        }
        return aspect
            
    def _showAspectButtons(self):
        loaded = self.variant_frame.winfo_children()
        if loaded:
            return

        variants = [
            (page.ATTRIB_IMAGE, msg.PDF_ATTRIB_IMAGE),
            (page.SINGLE, msg.PDF_SINGLE),
            (page.WIDE, msg.PDF_WIDE),
            (page.DOUBLE, msg.PDF_DOUBLE),
            (page.QUART, msg.PDF_QUART),
            (page.TRIPLE, msg.PDF_TRIPLE),
            (page.BIG, msg.PDF_BIG),
            (page.FULL, msg.PDF_FULL),
            (page.HALF, msg.PDF_HALF)
        ]

        for variant in variants:
            button = tk.Button(
                self.variant_frame,
                text=variant[1],
                anchor=tk.W
            )
            button.bind("<Button-1>", self._aspectSelector)
            button.pack(fill=tk.X)
        self.variants = variants
        self.variant_frame.pack(fill=tk.X)

    # the player clicked on one of the aspect buttons ...
    def _aspectSelector(self, event):
        self.finished = 0
        widget = event.widget

        # update buttons and retrieve selection ...
        buttons = self.variant_frame.winfo_children()
        for button in buttons:
            button.config(background="#eeeeee")
            if button is widget: 
                text = button.cget("text")
                for variant in self.variants:
                    if variant[1] == text:
                        self.selected_size = variant[0]
        widget.config(background="#ffffaa")

        self.selected_ratio = self._aspectRatios()[self.selected_size]

        # remove current selector ...        
        if self.rect is not None:
            self.image_canvas.delete(self.rect)
            self.rect = None
        # ... and create a new one ... 
        if self.rect is None:
            border = 5
            img_bbox = self.image_canvas.bbox(self.img_on_canvas)
            ratio = 1.0 * (img_bbox[2] - img_bbox[0]) / (img_bbox[3] - img_bbox[1])
            width = img_bbox[2] - img_bbox[0]
            height = img_bbox[3] - img_bbox[1]
            half_x = img_bbox[0] + 0.5 * width
            half_y = img_bbox[1] + 0.5 * height
            
            image_tag = self.char.getImage()
            if image_tag is not None:
                size_tag = image_tag.find("size[@name='"+self.selected_size+"']")

                # load stored selection
                if size_tag is not None:
                    x1 = float(size_tag.get("x", "0")) * width
                    y1 = float(size_tag.get("y", "0")) * height
                    while y1 <= 0:
                        y1 += 1
                    while x1 <= 0:
                        x1 += 1
                    scale = float(size_tag.get("scale", "1"))
                    box_width = 1.0 * scale * width - 5
                    while x1 + box_width >= width:
                        box_width -= 1
                    box_height = 1.0 * box_width / self.selected_ratio - border
                    x2 = x1 + box_width
                    y2 = y1 + box_height

                    # translate according to image positon 
                    x1 += img_bbox[0] + 0.5 * border
                    y1 += img_bbox[1] + 0.5 * border
                    x2 += img_bbox[0] + 0.5 * border
                    y2 += img_bbox[1] + 0.5 * border
                # or create new selection
                elif ratio > self.selected_ratio:
                    box_width = 1.0 * height * self.selected_ratio
                    x1 = int(half_x - 0.5 * box_width)
                    y1 = img_bbox[1]
                    x2 = int(half_x + 0.5 * box_width)
                    y2 = img_bbox[3]
                elif ratio <= self.selected_ratio:
                    box_height = 1.0 * width / self.selected_ratio
                    x1 = img_bbox[0]
                    y1 = int(half_y - 0.5 * box_height)
                    x2 = img_bbox[2]
                    y2 = int(half_y + 0.5 * box_height)

                # draw selection box ... 
                self.rect = self.image_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="",
                    outline="#ffff00",
                    width=border)

                # store selection box ..
                self._setFinished()
                self._updateBoundingBox()
                    
    # this may look like overkill but it is necessary ... :D    
    def _setFinished(self):
        self.finished = 1

    # event handler to move the selection frame ...               
    def _moveFrame(self, event):
        """ This event handler is responsible for moving the selection frame
        event: tk.event ...
        """

        self.finished = 0
        dx = 0
        dy = 0

        # mouse based movement ...         
        x = event.x
        y = event.y
        if self.x is not None and self.y is not None:
            dx = x - self.x
            dy = y - self.y

        # keyboard movement ...
        if event.keysym == "Left":
            dx = -2
            dy = 0
        elif event.keysym == "Up":
            dx = 0
            dy = -2
        elif event.keysym == "Right":
            dx = 2
            dy = 0
        elif event.keysym == "Down":
            dx = 0
            dy = 2

        if self.rect is not None:
            self.image_canvas.itemconfig(self.rect, outline="#ffff00")

            # retrieve current position of image and selection box ... 
            rect_box = self.image_canvas.bbox(self.rect)
            image_box = self.image_canvas.bbox(self.img_on_canvas)

            rect_width = rect_box[2] - rect_box[0]
            rect_height = rect_box[3] - rect_box[1]

            image_width = image_box[2] - image_box[0]
            image_height = image_box[3] - image_box[1]

            image_center_x = image_box[0] + image_width * 0.5
            image_center_y = image_box[1] + image_height * 0.5

            left_margin = rect_box[0] - image_box[0]
            right_margin = image_box[2] - rect_box[2]
            top_margin = rect_box[1] - image_box[1]
            bottom_margin = image_box[3] - rect_box[3]

            # make sure the selection does not expand over the image borders
            if dx < 0 and abs(dx) > left_margin:
                dx = -left_margin
            if dx > right_margin: dx = right_margin
            if dy < 0 and abs(dx) > top_margin <= 5:
                dy = -top_margin
            if dy > bottom_margin: dy = bottom_margin

            # actually move the selection box
            self.image_canvas.move(self.rect, dx, dy)

        self.x = x
        self.y = y

        self.image_canvas.after(100, self._setFinished)
        if self.update == 0:
            self.image_canvas.after(1500, self._updateBoundingBox)
            self.update = 1

    def _scaleFrame(self, event):
        self.finished = 0
        if self.rect is not None:
            self.image_canvas.itemconfig(self.rect, outline="#ffff00")
            rect_box = self.image_canvas.bbox(self.rect)
            image_box = self.image_canvas.bbox(self.img_on_canvas)

            rect_width = rect_box[2] - rect_box[0]
            rect_height = rect_box[3] - rect_box[1]

            image_width = image_box[2] - image_box[0]
            image_height = image_box[3] - image_box[1]

            image_center_x = image_box[0]+image_width*0.5
            image_center_y = image_box[1]+image_height*0.5

            left_margin = rect_box[0] - image_box[0]
            right_margin = image_box[2] - rect_box[2]
            top_margin = rect_box[1] - image_box[1]
            bottom_margin = image_box[3] - rect_box[3]

            # set soft scale centers ... 
            scale_center_x = image_center_x + left_margin - right_margin
            scale_center_y = image_center_y + top_margin - bottom_margin
                 
            if event.char == "+":
                if (rect_width < 0.99 * image_width
                    and rect_height < 0.99 * image_height
                ):
                    self.image_canvas.scale(
                        self.rect,
                        scale_center_x,
                        scale_center_y,
                        1.01,
                        1.01
                    )

                    if left_margin <= 5:
                        self.image_canvas.move(self.rect, 1, 0)
                    if right_margin <= 5:
                        self.image_canvas.move(self.rect, -1, 0)
                    if top_margin <= 5:
                        self.image_canvas.move(self.rect, 0, 1)
                    if bottom_margin <= 5:
                        self.image_canvas.move(self.rect, 0, -1)

            if event.char == "-":
                self.image_canvas.scale(
                    self.rect,
                    scale_center_x,
                    scale_center_y,
                    0.99,
                    0.99
                )
               
            self.image_canvas.after(100, self._setFinished)
            if self.update == 0:
                self.image_canvas.after(1500, self._updateBoundingBox)
                self.update = 1

    def _stopMotion(self, event):
        self.x = None
        self.y = None

    def _updateBoundingBox(self):
        self.update = 0
        if self.finished == 1:
            if self.rect is not None:
                # bbox DEFIN
                image_tag = self.char.getImage()

                rect_box = self.image_canvas.bbox(self.rect)
                image_box = self.image_canvas.bbox(self.img_on_canvas)

                image_width = image_box[2] - image_box[0]
                image_height = image_box[3] - image_box[1]

                rect_width = rect_box[2] - rect_box[0]
                x = 1.0 * (rect_box[0]-image_box[0]) / image_width
                y = 1.0 * (rect_box[1]-image_box[1]) / image_height
                scale = 1.0 * rect_width / image_width

                self.char.setImageSize(
                    self.selected_size,
                    x,
                    y,
                    scale
                )
                self.image_canvas.itemconfig(
                    self.rect,
                    outline="#00dd00"
                )

    # this defines the load / remove button for an image ... 
    def _checkForImage(self):
        """ check if an image file is defined in the character xml and set
        the button for importing or deleting an image """

        image_tag = self.char.getImage()
        if image_tag is not None:
            self.load_button.config(
                text=msg.IS_REMOVE_IMAGE,
                command=self._removeImage
            )
        else:
            self.load_button.config(
                text=msg.IS_IMPORT_IMAGE,
                command=self.loadImageWindow
            )

    # remove the image
    def _removeImage(self):
        """ this method removes the character image and redraws the ImageScreen
        """
        self.char.removeImage()
        self.image_canvas.delete(tk.ALL)
        self._checkForImage()

    # TEST - Export alle Bildmodule ... 
    def _test(self):
        """ exporting a test PDF displaying the image in all module sizes 
        """
        template = et.Element("template")
        page1 = et.SubElement(template,"page",{"num":"1"})
        et.SubElement(page1,"module",{"row":"0", "col":"2", "size":"single","type":"image","id":"1"})
        et.SubElement(page1,"module",{"row":"0", "col":"1", "size":"double","type":"image","id":"2"})
        et.SubElement(page1,"module",{"row":"0", "col":"0", "size":"double","type":"attributes","id":"3"})
        et.SubElement(page1,"module",{"row":"1", "col":"2", "size":"triple","type":"image","id":"4"})
        et.SubElement(page1,"module",{"row":"0", "col":"3", "size":"full","type":"image","id":"5"})
        et.SubElement(page1,"module",{"row":"2", "col":"0", "size":"quart","type":"image","id":"6"})
        page2 = et.SubElement(template,"page",{"num":"1"})
        et.SubElement(page2,"module",{"row":"0", "col":"0", "size":"wide","type":"image","id":"7"})
        et.SubElement(page2,"module",{"row":"1", "col":"0", "size":"big","type":"image","id":"8"})
        et.SubElement(page2,"module",{"row":"0", "col":"2", "size":"half","type":"image","id":"9"})

        exportpdf.ExportPdf("test.pdf",self.char,self.app.traits,template)


