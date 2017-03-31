import os
import xml.etree.ElementTree as et
import tkinter as tk


class TraitTree(object):
    """ Provides an ElementTree with character Traits"""

    def __init__(self, settings):
        self.xml_traits = self.loadTree("data/traits_de.xml")

        self.settings = settings

    def loadTree(self, filename=None):
        """ Getting the traits from a given filename """
        tree = None
        if not filename:
            return tree

        with open(filename, mode="rb") as file:
            try:
                tree = et.parse(filename)
                root = tree.getroot()
                if root.tag == "expansion":
                    traits = root.find("traits")
                    tree = et.ElementTree(traits)
            except et.ParseError as e:
                print(str(e))

        return tree

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
