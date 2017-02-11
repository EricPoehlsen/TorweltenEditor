import tkinter as tk


class ToolTip(tk.Toplevel):
    def __init__(
            self,
            *args,
            event=None,
            message=None,
            delay=2500,
            screentime=250,
            **kwargs
    ):
        tk.Toplevel.__init__(self, *args, **kwargs)

        if message is None:
            self.destroy()

        self.event = event
        self.message = message
        self.delay = delay
        self.screentime = screentime

        self.overrideredirect(True)
        self.geometry("1x1+1+1")

        # initial mouse position
        self.x, self.y = self.winfo_pointerxy()

        # start countdown
        self.active_call = self.after(delay, self._display)

    # show the tooltip
    def _display(self):
        # current mouse position
        x, y = self.winfo_pointerxy()

        # are we still on the widget?
        widget = self.event.widget
        x1 = widget.winfo_rootx()
        y1 = widget.winfo_rooty()
        x2 = x1 + widget.winfo_width()
        y2 = y1 + widget.winfo_height()

        if x1 < x < x2 and y1 < y < y2:
            # draw the tooltip to the screen
            msg_label = tk.Label(
                self,
                text=self.message,
                background="#ffff99",
                relief=tk.GROOVE)
            msg_label.pack()

            width = msg_label.winfo_reqwidth()
            height = msg_label.winfo_reqheight()
            
            x_pos = x - (width/2)
            y_pos = y - height + 5

            placement = "{width}x{height}+{x}+{y}".format(
                width=width,
                height=height,
                x=int(x_pos),
                y=int(y_pos)
            )
            self.geometry(placement)
            
            self.bind("<Leave>", lambda e: self.destroy())
        else:
            self.destroy()
