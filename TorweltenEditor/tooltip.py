# coding=utf-8
import tkinter as tk

class ToolTip(tk.Canvas):
    def __init__(self, *args, event = None, message = None, delay=1500, screentime=250 ,threshold = 50, **kwargs):
        tk.Canvas.__init__(self, *args,**kwargs)
        self.__name__ = self.winfo_name()    

        
        
        self.event = event

		# store variables
        self.args = args
        self.kwargs = kwargs
        self.threshold = threshold
        self.message = message
        self.delay = delay
        self.screentime = screentime
        self.event = event
        
		# initial mouse position
        self.x, self.y = self.winfo_pointerxy()

        # unbinding the calling event!
        # this feels dirty ... 
        if self.event is not None: 
            widget = self.event.widget
            event_type = "<"+self.event.type+">"
            widget.unbind(event_type)

		# start countdown
        self.active_call = self.after(delay,self._display)
        self.active_check = None

	# show the tooltip
    def _display(self):
		# current mouse position
        x, y = self.winfo_pointerxy()

		# check if within threshold ...
        if (x in range(self.x-self.threshold,self.x+self.threshold) and
            y in range(self.y-self.threshold,self.y+self.threshold)):
            
            # draw the tooltip to the screen 
            msg_label = tk.Label(self, text=self.message, background="#ffff99",relief = tk.GROOVE)
            msg_label.pack()

            width = msg_label.winfo_reqwidth()
            height = msg_label.winfo_reqheight()
            
            toplevel = self.winfo_toplevel()
            top_x = toplevel.winfo_rootx()
            top_y = toplevel.winfo_rooty()

            x_pos = x - top_x - (width/2)
            y_pos = y - top_y - height
            
            self.place(x=x_pos, y=y_pos)
            
            self.active_check = self.after(self.screentime,self._checkMousePos)

        else:
            self.destroy()

	# check if tooltip is to remove ... 
    def _checkMousePos(self):
        self.active_check = None

        ## define the extended bounding box .. 
        x_min = self.winfo_rootx() - self.threshold
        x_max = self.winfo_rootx() + self.winfo_width() + self.threshold
        y_min = self.winfo_rooty() - self.threshold
        y_max = self.winfo_rooty() + self.winfo_height() + self.threshold
        
        #print(x_min,y_min)
        x, y = self.winfo_pointerxy()

        # destroy if threshold left ... 
        if x not in range(x_min,x_max) or y not in range(y_min,y_max):
            self.destroy()
        else:
            self.active_check = self.after(self.screentime,self._checkMousePos)

    # also desperates measures
    def destroy(self):
        if self.active_call is not None:
            self.after_cancel(self.active_call)
        if self.active_check is not None: 
            self.after_cancel(self.active_check)
        tk.Canvas.destroy(self)

        # rebinding the event (this is so dirty :/)
        if self.event is not None:
            widget = self.event.widget
            event_type = "<"+self.event.type+">"
            widget.bind(event_type, lambda event: ToolTip(*self.args,**self.kwargs))
