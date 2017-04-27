# coding=utf-8
import tkinter as tk
import config
import os
import xml.etree.ElementTree as et

msg = config.Messages()

"""
FOR LATER USE 
members = [attr for attr in dir(msg) if not attr.startswith("__")]
print(members)
"""


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

        self.basic_frame = self.coreSettings(self)
        self.basic_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def coreSettings(self, parent):
        frame = tk.LabelFrame(parent, text=msg.SET_CORE_SETTINGS)
        init_xp = self.initialXPEntry(frame)
        init_xp.pack(fill=tk.X, expand=1)

        expansions = self.expansionsFrame(frame)
        expansions.pack(fill=tk.X, expand=1)

        tk.Button(
            frame,
            text=msg.ME_SAVE,
            command=self.save
        ).pack()

        return frame

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

    def expansionsFrame(self, parent):
        """ building the data selection frame """

        self.scanDataFiles()
        frame = tk.LabelFrame(parent, text=msg.SET_EXPANSIONS)
        cur_selection = self.settings.getExpansions()
        print(cur_selection)
        for name, lang, file in self.data["expansions"]:
            self.data["exp_"+file] = var = tk.IntVar()
            button = tk.Checkbutton(
                frame,
                text=name + " " + file,
                offvalue=0,
                onvalue=1,
                var=var,
            )
            var.set(0)
            if file in cur_selection:
                var.set(1)
            button.pack(anchor=tk.W, expand=1)
        return frame

    def scanDataFiles(self):
        """ find available expansions """

        self.data["expansions"] = []
        path = "expansion/"

        files = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            files.extend(filenames)
            break

        for file in files:
            if file.endswith("xml"):
                filename = path+file
                try:
                    xml_tree = et.parse(filename)
                    root = xml_tree.getroot()
                    tag = root.tag
                    if tag == "expansion":
                        meta = root.find("meta")
                        if meta is not None:
                            name = root.get("name", "")
                            lang = meta.get("lang")
                            self.data["expansions"].append((name, lang, file))
                except et.ParseError:
                    print(file + "error")

    def updateDataSources(self):
        for expansion in self.data["expansions"]:
            var = self.data["exp_"+expansion[2]]
            selected = var.get()
            if selected:
                self.settings.updateExpansions(expansion[2], include=True)
            else:
                self.settings.updateExpansions(expansion[2], include=False)

    def save(self):
        """ saving settings """

        new_initial_xp = self.data["init_xp"].get()
        self.settings.setInitialXP(new_initial_xp)
        self.updateDataSources()

        self.settings.save()
