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

        label = tk.Label(
            self,
            text=msg,
            bg="#ffffe0",
            fg="#555533",
            relief=tk.SOLID,
            borderwidth=1,
        )
        label.pack(anchor=tk.S)
        geometry = "+{x}+{y}".format(
            x=x,
            y=y - label.winfo_reqheight() - 5
        )
        self.geometry(geometry)
