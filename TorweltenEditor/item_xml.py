# coding=utf-8

import xml.etree.ElementTree as et
import config

it = config.ItemTypes()


class ItemTree(object):
    def __init__(self):
        # this is the xml interpretation of the available items
        self.xml_items = None
        self.loadTree()
        self.EQUIPPABLE = [
            it.CLOTHING,
            it.BAG,
            it.CONTAINER,
            it.BOX,
            it.HARNESS,
            it.ARMOR,
            it.CLUBS,
            it.BLADES,
            it.STAFFS,
            it.OTHER_MELEE,
            it.PISTOLS,
            it.REVOLVERS,
            it.RIFLES,
            it.SHOT_GUNS,
            it.RIFLES_SA,
            it.RIFLES_SA,
            it.AUTOMATIC_PISTOLS,
            it.AUTOMATIC_RIFLES,
            it.MASCHINE_GUNS,
            it.TOOLS,
            it.NATURAL,
        ]
                           
    def loadTree(self, filename=None):
        if filename is None:
            try: 
                self.xml_items = et.parse('data/items.xml')
            except (et.ParseError, IOError) as error:
                print(error)
        else: 
            try: 
                module = et.parse(filename)
            except (et.ParseError, IOError) as error:
                print(error)

    def getGroup(self,group_name):
        result = list()
        group = self.xml_items.find("./group[@name='"+group_name+"']")
        subgroups = group.findall("./group")
        for subgroup in subgroups:
            result.append(subgroup)
        return result

    def getGroups(self):
        return self.xml_items.findall(".//group")

    def getAllItems(self):
        return self.xml_items.findall(".//item")

    def getItems(self, group_name):
        group = self.xml_items.find(".//group[@name='"+group_name+"']")
        items = group.findall("./item")
        return items

    def getItem(self,name):
        skill = self.xml_skills.find(".//item[@name='"+name+"']") 
        return skill

