# coding=utf-8

import os
import xml.etree.ElementTree as et
import tkinter as tk

class TraitTree():
    def __init__(self):
        # this is the xml interpretation of the character
        self.xml_traits = None
        self.loadTree()

    def loadTree(self,filename = None):
        self.xml_traits = et.parse('data/traits.xml')


    # get a string list of all traits by name 
    def list(self):
        result = list()

        traits = self.xml_traits.findall("trait")
        for trait in traits:
            name = trait.get("name")
            result.append(name)
        return result

    def fullList(self):
        result = list()

        traits = self.xml_traits.findall("trait")
        for trait in traits:
            name = trait.get("name")
            cls = trait.get("class")
            grp = trait.get("group")
            result.append((name,cls,grp))
        return result
    
    # get a trait by its name
    def getTrait(self,name):
        trait = self.xml_traits.find("trait[@name='"+name+"']") 
        return trait

