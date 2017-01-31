# coding=utf-8
import tkinter as tk
import config

class SettingScreen(tk.Frame):
    def __init__(self,main,app):
        tk.Frame.__init__(self,main)
        self.app = app
        self.char = app.char

        self.mode_frame = tk.LabelFrame(self, text = "Modus wechseln")
        self.mode_frame.pack()

        self.edit_mode = tk.StringVar()
        self.edit_mode.set(self.char.getEditMode())

        self.gen_rb = tk.Radiobutton(self.mode_frame,text = "Charaktererschaffung", variable = self.edit_mode, value = "generation", command = self.editModeChanged)
        self.gen_rb.pack(anchor = tk.W)
        self.edit_rb = tk.Radiobutton(self.mode_frame,text = "Bearbeitung", variable = self.edit_mode, value = "edit", command = self.editModeChanged)
        self.edit_rb.pack(anchor = tk.W)
        self.sim_rb = tk.Radiobutton(self.mode_frame,text = "Simulation", variable = self.edit_mode, value = "simulation", command = self.editModeChanged)
        self.sim_rb.pack(anchor = tk.W)
        self.view_rb = tk.Radiobutton(self.mode_frame,text = "Ansicht", variable = self.edit_mode, value = "view", command = self.editModeChanged)
        self.view_rb.pack(anchor = tk.W)
        self.editModeChanged()

    def editModeChanged(self):
        mode = self.edit_mode.get()
        if mode == "generation":self.gen_rb.select()
        elif mode == "edit":self.edit_rb.select()
        elif mode == "simulation":self.sim_rb.select()
        elif mode == "view":self.view_rb.select()
        self.char.setEditMode(mode)


