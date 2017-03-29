# coding=utf-8
import tkinter as tk
import config

msg = config.Messages()


class SettingScreen(tk.Frame):
    def __init__(self, main, app):
        tk.Frame.__init__(self, main)
        self.app = app
        self.char = app.char
        self.settings = app.settings
        self.data = {}

        self.config(
            width=app.main_frame.winfo_reqwidth(),
            height=app.main_frame.winfo_reqheight()
        )

        print(self.winfo_reqwidth(), self.winfo_reqheight())
        self.char_settings = self.charSettings(self)
        self.char_settings.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.basic_frame = self.coreSettings(self)
        self.basic_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def charSettings(self, parent):
        frame = tk.LabelFrame(parent, text=msg.SET_CHAR_SETTINGS)

        editmode = self.editModeSwitcher(frame)
        editmode.pack()

        return frame

    def coreSettings(self, parent):
        frame = tk.LabelFrame(parent, text=msg.SET_CORE_SETTINGS)
        init_xp = self.initialXPEntry(frame)
        init_xp.pack(fill=tk.X, expand=1)

        tk.Label(frame, text="Test").pack()

        tk.Button(
            frame,
            text=msg.ME_SAVE,
            command=self.save
        ).pack()
        return frame

    def editModeSwitcher(self, parent):
        var = self.data["editmode"] = tk.StringVar()

        frame = tk.LabelFrame(parent, text=msg.SET_EDIT_MODE)
        modes = [
            (msg.SET_EDIT_GENERATION, "generation"),
            (msg.SET_EDIT_EDIT, "edit"),
            (msg.SET_EDIT_VIEW, "view"),
            (msg.SET_EDIT_SIM, "simulation")
        ]
        for txt, val in modes:
            button = tk.Radiobutton(
                frame,
                text=txt,
                variable=var,
                value=val,
            )
            button.deselect()
            button.pack(anchor=tk.W)

        var.set(self.char.getEditMode())
        switch = tk.Button(
            frame,
            text=msg.SET_EDIT_SWITCH,
            command=self.setEditMode
        )
        switch.pack(fill=tk.X)

        return frame

    def setEditMode(self):
        mode = self.data["editmode"].get()
        self.char.setEditMode(mode)

    def initialXPEntry(self, parent):
        """ create an entry for the initial XP """

        frame = tk.LabelFrame(parent, text=msg.SET_INITIAL_XP)
        var = self.data["init_xp"] = tk.StringVar()
        var.set(self.settings.getInitialXP())
        entry = tk.Entry(frame, textvariable=var)
        var.trace("w", lambda n, e, m: self.checkInitialXP())
        entry.pack(fill=tk.X)
        return frame

    def checkInitialXP(self):
        """ tracing the initial XP value and fixing illegal entries """

        val = self.data["init_xp"].get()
        try:
            val = int(val)
            if val < 0:
                raise ValueError
        except ValueError:
            self.data["init_xp"].set("0")

    def save(self):
        """ saving settings """

        new_initial_xp = self.data["init_xp"].get()
        self.settings.setInitialXP(new_initial_xp)

        self.settings.save()
