# coding=utf-8
import config
import random
from PIL import ImageTk,Image,PngImagePlugin
import tkinter as tk

class EWTScreen(tk.Frame):
    def __init__(self,main,app):
        tk.Frame.__init__(self,main)
        self.app = app
        self.char = app.char

        self.ewt00 = ImageTk.PhotoImage(file="img/ewt_00.png")
        self.ewt05 = ImageTk.PhotoImage(file="img/ewt_05.png")
        self.ewt10 = ImageTk.PhotoImage(file="img/ewt_10.png")
        self.ewt20 = ImageTk.PhotoImage(file="img/ewt_20.png")

        # this var holds the entry field ...
        self.roll_var = tk.StringVar()

        # setting up the frames
        self.left_frame = tk.Frame(self)
        self.ewt_frame = tk.Frame(self.left_frame)
        self.showEWT(self.ewt_frame)
        self.ewt_frame.pack()

        self.roll_frame = tk.Frame(self.left_frame)
        self.showRollFrame(self.roll_frame)
        self.roll_frame.pack(fill = tk.X)

        self.left_frame.pack(side = tk.LEFT)

        self.result_frame = tk.Frame(self)
        self.result_frame.pack(side = tk.LEFT, anchor = tk.N)
        
    # display the EWT
    def showEWT(self,frame):
        """ This method draws the EWT using graphics 
        frame: tk.Frame() target to draw in ...
        
        The frame will not be cleared! 
        This method uses the grid geometry manager 
        on 11 rows and 17 columns!
        """

        rolls = [1,2,3,4,5,6,7,8,9,10]
        columns = [-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7]
        for column in columns: 
            label = tk.Label(frame, text = column, font = "sans 12 bold")
            label.grid(row = 0, column = column + 8)

        for roll in rolls:
            label = tk.Label(frame, text = roll, font = "sans 12 bold")
            label.grid(row = roll, column = 0)
            label = tk.Label(frame, text = roll, font = "sans 12 bold")
            label.grid(row = roll, column = 16)
            label = tk.Label(frame, text = roll)
            for column in columns:
                rowindex = roll - 1
                colindex = column + 7
                effect = config.EWT[rowindex][colindex]
                image = None
                if effect == 0.0: image = self.ewt00
                elif effect == 0.5: image = self.ewt05
                elif effect == 1.0: image = self.ewt10
                elif effect == 2.0: image = self.ewt20
                label = tk.Label(frame, 
				                 image = image, 
								 padx = 1,
								 pady = 1, 
								 highlightbackground = "#000000")
                if rowindex%2 == 0: label.config(background = "#cccccc")
                else: label.config(background = "#eeeeee")
                label.image = image
                label.grid(row = rowindex + 1, column = colindex + 1)

    # user input for roll ...
    def showRollFrame(self,frame):
        """ This method displays an entry field and a button and binds _rollEWT() as event
        frame: target tk.Frame()

        The frame will not be cleared, the pack geometry manager is used.
        """
        entry = tk.Entry(frame, font = "sans 20 bold", textvariable = self.roll_var, justify = tk.CENTER)
        entry.bind("<Return>",self._rollEWT)
        entry.pack(fill = tk.X, side = tk.LEFT, expand = 1)
        button = tk.Button(frame, text = "Würfeln")
        button.bind("<Button-1>",self._rollEWT)
        button.pack(fill = tk.Y, side = tk.LEFT)

    # event based call for rollEWT()    
    def _rollEWT(self,event):
        """ This internal method handles the event from the entry field and button,
        calls rollEWT() and displays the result using showResults()! 
        """
        ewt_string = self.roll_var.get()
        parts = ewt_string.split("/")
        
        # sanitize input ... 
        if len(parts) != 2: 
            parts = [1,0]
            self.roll_var.set("1/0")
        try:
            parts[0] = int(parts[0])
            if parts[0] < 1: raise ValueError
            parts[1] = int(parts[1])
            if not -7 <= parts[1] <= 7: raise ValueError
        except ValueError:
            parts = [1,0]
            self.roll_var.set("1/0")

        # make the rolls ...
        results = self.rollEWT(parts[0],parts[1],True)
        self.showResults(self.result_frame,results)
    
    # show the result of the roll
    def showResults(self,frame,results):
        """ display the results of an EWT roll using graphics
        frame: a tk.Frame() to display the results in (will be cleared on each call)
        results: expects the results of rollEWT(..,transparent=True)!
        """
        # clear frame
        widgets = frame.winfo_children()
        for widget in widgets: widget.destroy()

        # load images from disk 
        d = {}
        ewt = {}

        try: 
            d[1] = ImageTk.PhotoImage(file="img/d1.png")
            d[2] = ImageTk.PhotoImage(file="img/d2.png")
            d[3] = ImageTk.PhotoImage(file="img/d3.png")
            d[4] = ImageTk.PhotoImage(file="img/d4.png")
            d[5] = ImageTk.PhotoImage(file="img/d5.png")
            d[6] = ImageTk.PhotoImage(file="img/d6.png")
            d[7] = ImageTk.PhotoImage(file="img/d7.png")
            d[8] = ImageTk.PhotoImage(file="img/d8.png")
            d[9] = ImageTk.PhotoImage(file="img/d9.png")
            d[10] = ImageTk.PhotoImage(file="img/d0.png")

            ewt["0"] = ImageTk.PhotoImage(file="img/ewt_00.png")
            ewt["/"] = ImageTk.PhotoImage(file="img/ewt_05.png")
            ewt["x"] = ImageTk.PhotoImage(file="img/ewt_10.png")
            ewt["x+"] = ImageTk.PhotoImage(file="img/ewt_20.png")

        except IOError:
            d = {1:"1"}
            ewt = {"0":"O","/":"/","x":"x","X+":"X+"}

        # last roll header ... 
        last_roll = self.roll_var.get()
        parts = last_roll.split("/")
        if int(parts[1]) > 0: parts[1] = "+"+str(parts[1])
        if parts[1] == "0": parts[1] = "±0"
        tk.Label(frame,text = "Letzter Wurf: "+parts[0]+"/"+parts[1], justify = tk.LEFT,font = "sans 10 bold").pack(anchor = tk.W)

        roll = 1
        sum = 0

        for result in results:
            roll_frame = tk.Frame(frame)
            if result[1] == 0.0: effect = ewt["0"]
            if result[1] == 0.5: effect = ewt["/"]
            if result[1] == 1.0: effect = ewt["x"]
            if result[2]: text = effect = ewt["x+"]
            else: roll += 1
            

            # if graphics exist ... 
            if d[1] != "1" and ewt["0"] != "O":
                dice = d[result[0]]
                dice_img = tk.Label(roll_frame,image = dice)
                dice_img.image = dice
                dice_img.pack(side = tk.LEFT)
                colon = tk.Label(roll_frame, text = " : ", font = "sans 16 bold")
                colon.pack(side = tk.LEFT)
                effect_img = tk.Label(roll_frame, image = effect)
                effect_img.image = effect
                effect_img.pack(side = tk.LEFT)
            else:
                text = "Wurf: "+str(result[0]) + " - Effekt: "+effect
            
            roll_frame.pack()
            sum += result[1]

        tk.Label(frame,text = "Gesamteffekt: "+str(sum),justify = tk.LEFT,font = "sans 10 bold").pack(anchor = tk.W)


    # make a roll on the EWT
    def rollEWT(self,dice = 1,column = 0,transparent = False):
        """ This method handles a (blackbox) check against the EWT.
        dice: int >= 1 - number of dice to roll 
        column: int [-7:7] - column to roll against ...
        transparent: if True the second return will be produced ... 
            Any out of bound entries will be sanitized to 1/0 rolls
        return: float - accumulated roll result ...  
        return: [(roll,result,reroll),...]
                roll = int 1-10
                result = float 0.0,0.5,1.0
                reroll = bool (True if this roll warranted a reroll)

        """

        # cleaning up input ... 
        try: 
            dice = int(dice)
            if dice < 1: dice = 1
        except ValueError: 
            dice = 1

        try: 
            column = int(column)
            if not -7 <= column <= 7: column = 0
        except ValueError:
            column = 0

        # transpose column ...
        column = column + 7
        
        # initialize randomizer
        random.seed()

        # initialize result
        result = 0.0
        if transparent: result = []

        # roll while dice are available
        rolls = dice
        while rolls > 0: 
            # make the roll
            roll = random.randint(1,10)

            # get the result from table
            roll_result = config.EWT[roll-1][column]
            
            reroll = False
            # handle rerolls
            if roll_result == 2.0:
                roll_result = 1.0
                rolls += 1
                reroll = True
            
            # write result and reduce number of rolls
            if transparent: result.append((roll,roll_result,reroll))
            else: result = result + roll_result
            rolls -= 1
            
        return result         