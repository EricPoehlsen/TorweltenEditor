import os
import xml.etree.ElementTree as et
import tkinter as tk


class Settings(object):
    def __init__(self):
        # this is the xml interpretation of the character
        self.xml_settings = None
        self.load()

    def load(self):
        """ loads settings - if not found create new """

        try:
            self.xml_settings = et.parse("settings.xml")
        except FileNotFoundError:
            self.new()

    def save(self):
        """ save current settings """

        with open("settings.xml", mode="wb") as file:
            self.xml_settings.write(file, encoding="utf-8", xml_declaration=True)

        self.load()

    def new(self):
        """ creates a new blanc setting template """

        settings = et.Element("settings")
        system = et.SubElement(settings, "system")
        et.SubElement(system, "language", {"value": "de"})
        data = et.SubElement(system, "expansions")
        generation = et.SubElement(settings, "generation", {"xp": "300"})

        self.xml_settings = et.ElementTree(settings)

    def getInitialXP(self):
        """ retrieve the initial XP for character generation. """

        return self.xml_settings.find("generation").get("xp")

    def setInitialXP(self, value):
        """ update the initial XP for character generation. """

        gen_settings = self.xml_settings.find("generation")
        gen_settings.set("xp", str(value))

    def getExpansions(self):
        filenames = None
        expansions = self.xml_settings.findall("./system/expansions/expansion")
        filenames = []
        for entry in expansions:
            filenames.append(entry.get("file"))

        return filenames

    def updateExpansions(self, filename=None, include=False):
        if not filename:
            return

        data = self.xml_settings.find("./system/expansions")
        element = data.find("./expansion[@file='"+filename+"']")
        if include:
            if element is None:
                et.SubElement(data, "expansion", {"file": filename})
        else:
            if element is not None:
                data.remove(element)

