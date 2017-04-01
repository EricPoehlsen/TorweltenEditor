import os
import xml.etree.ElementTree as et
import tkinter as tk


class TraitTree(object):
    """ Provides an ElementTree with character Traits"""

    def __init__(self, settings):
        self.xml_traits = None
        self.settings = settings
        self.buildTree()

    def loadTree(self, filename=None):
        """ Getting the traits from a given filename """
        tree = None
        if filename:
            try:
                tree = et.parse(filename)
                root = tree.getroot()
                if root.tag == "expansion":
                    traits = root.find("traits")
                    if traits is not None:
                        tree = et.ElementTree(traits)
                    else:
                        tree = None
            except (FileNotFoundError, et.ParseError) as e:
                print(str(e))

        return tree

    def addToTree(self, filename=None):
        """ Adding another set of traits to the trait tree

        Args:
            filename (str): the file to parse
        """

        if filename is None:
            return

        local_tree = self.loadTree(filename)
        if local_tree is None:
            return

        traits = local_tree.findall(".//trait")
        for trait in traits:
            name = trait.get("name")
            existing_trait = self.getTrait(name)
            if existing_trait is None:
                loaded_traits = self.xml_traits.getroot()
                loaded_traits.append(trait)

    def buildTree(self):
        self.xml_traits = self.loadTree("data/traits_de.xml")
        active_expansions = self.settings.getExpansions()
        for expansion in active_expansions:
            self.addToTree("data/" + expansion)

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
