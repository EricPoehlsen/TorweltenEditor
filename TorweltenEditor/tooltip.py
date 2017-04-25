import tkinter as tk
from PIL import ImageTk


class ToolTip(object):
    def __init__(self, widget, msg, variant=None):
        self.widget = widget
        self.msg = msg
        self.variant = variant
        self.id = None
        self.time = 1500
        self.tip = None
        self._bindings()

    def _bindings(self):
        self.widget.bind("<Enter>", self.start)
        self.widget.bind("<Leave>", self.stop)

    def start(self, event=None):
        self.id = self.widget.after(self.time, self.show)

    def stop(self, event=None):
        self.widget.after_cancel(self.id)
        if self.tip:
            self.tip.destroy()
            self.tip = None

    def update(self, msg=None, variant=None):
        self.msg = msg
        self.variant = variant

    def show(self):
        self.tip = Balloon(msg=self.msg, variant=self.variant)


class Balloon(tk.Toplevel):
    def __init__(self, *args, msg=None, variant=None, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

        if msg is None:
            self.destroy()

        self.overrideredirect(True)

        self.msg = msg
        self.icon = None

        self.background = "#fcfcfc"
        self.foreground = "#444444"
        if variant == "info":
            self.icon = ImageTk.PhotoImage(file="img/help_s.png")
            self.background = "#ddddff"
            self.foreground = "#000066"

        if variant == "error":
            self.icon = ImageTk.PhotoImage(file="img/exclamation_s.png")
            self.background = "#ffeecc"
            self.foreground = "#aa0000"

        if variant == "okay":
            self.icon = ImageTk.PhotoImage(file="img/tick_button_s.png")
            self.background = "#ddffcc"
            self.foreground = "#007700"

        x, y = self.winfo_pointerxy()
        frame = tk.Frame(
            self,
            bg=self.foreground,
        )
        frame.pack(anchor=tk.CENTER)
        label = tk.Label(
            frame,
            text=self.msg,
            bg=self.background,
            fg=self.foreground,
            justify=tk.LEFT,
            # relief=tk.SOLID,
            # borderwidth=1,
        )
        if self.icon:
            label.config(
                image=self.icon,
                compound=tk.LEFT
            )
        label.pack(anchor=tk.CENTER, padx=1, pady=1, ipadx=2, ipady=1)
        geometry = "+{x}+{y}".format(
            x=x,
            y=y + 24
        )
        self.geometry(geometry)
