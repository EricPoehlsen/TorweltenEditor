import config
from PIL import ImageTk
import tkinter as tk

msg = config.Messages()


class About(tk.Frame):
    """ The CharScreen displays the character on the main window

    Args:
        main (tk.Frame): the parent frame in which to display
        app (Application): the main application
    """

    def __init__(self, main, app):
        super().__init__(main)
        pass
