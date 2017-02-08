import os
import xml.etree.ElementTree as et
import tkinter as tk


class TraitTree(object):
    """ Provides an ElementTree with character Traits"""

    def __init__(self):
        self.xml_traits = None
        self.loadTree()

    def loadTree(self, filename="data/traits.xml"):
        """ Getting the traits from a given filename """

        with open(filename, mode="rb") as file:
            self.xml_traits = et.parse(file)

    def getTraits(self):
        """ get all traits

        Returns:
            Element<traits>: the root of traits
        """

        traits = self.xml_traits.getroot()
        return traits

    def getList(self):
        """ Retrieve a trait list

        Returns:
            [(name, class, groub),...]:
                name (str): name of trait
                class (str): class of trait
                group (str): group of trait
        """

        def listEntry(trait):
            name = trait.get("name")
            cls = trait.get("class")
            grp = trait.get("group")
            return name, cls, grp

        result = [listEntry(trait) for trait in self.getTraits()]
        return result
    
    def getTrait(self, name):
        """ Get a single trait by name

        Args:
            name(str): The name of the trait

        Returns:
            Element<trait>: the searched trait
            None: if not existing
        """

        trait = self.xml_traits.find("trait[@name='"+name+"']") 
        return trait
