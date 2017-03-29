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

        with open("setting.xml", mode="wb") as file:
            self.xml_settings.write(file, encoding="utf-8", xml_declaration=True)

    def new(self):
        """ creates a new blanc setting template """

        settings = et.Element("settings")
        system = et.SubElement(settings, "system")
        generation = et.SubElement(settings, "generation", {"xp": "300"})

        self.xml_settings = et.ElementTree(settings)

    def getInitialXP(self):
        """ retrieve the initial XP for character generation. """

        return self.xml_settings.find("generation").get("xp")

    def setInitialXP(self, value):
        """ update the initial XP for character generation. """

        gen_settings = self.xml_settings.find("generation")
        gen_settings.set("xp", str(value))
