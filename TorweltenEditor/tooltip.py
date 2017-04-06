import tkinter as tk


class ToolTip(object):
    def __init__(self, widget, msg):
        self.widget = widget
        self.msg = msg
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

    def show(self):
        self.tip = Balloon(msg=self.msg)


class Balloon(tk.Toplevel):
    def __init__(self, *args, msg=None, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)

        if msg is None:
            self.destroy()

        self.overrideredirect(True)

        x, y = self.winfo_pointerxy()
        frame = tk.Frame(
            self,
            bg="#444444",
        )
        frame.pack(anchor=tk.CENTER)
        label = tk.Label(
            frame,
            text=msg,
            bg="#fcfcfc",
            fg="#444444",
            # relief=tk.SOLID,
            # borderwidth=1,
        )
        label.pack(anchor=tk.CENTER, padx=1, pady=1, ipadx=2, ipady=1)
        geometry = "+{x}+{y}".format(
            x=x,
            y=y + 24
        )
        self.geometry(geometry)
