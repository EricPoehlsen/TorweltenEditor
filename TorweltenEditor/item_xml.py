import xml.etree.ElementTree as et
import config


it = config.ItemTypes()


class ItemTree(object):
    def __init__(self, settings):
        # this is the xml interpretation of the available items
        self.settings = settings
        self.xml_items = None
        self.buildTree()

        self.EQUIPPABLE = [
            it.CLOTHING,
            it.BAG,
            it.CONTAINER,
            it.BOX,
            it.HARNESS,
            it.ARMOR,
            it.CLUB,
            it.BLADE,
            it.STAFF,
            it.OTHER_MELEE,
            it.PISTOL,
            it.REVOLVER,
            it.RIFLE,
            it.SHOT_GUN,
            it.RIFLE_SA,
            it.AUTOMATIC_WEAPON,
            it.TOOLS,
            it.NATURAL,
        ]

    def buildTree(self):
        self.xml_items = self.loadTree('data/items_de.xml')
        active_expansions = self.settings.getExpansions()
        for expansion in active_expansions:
            self.addToTree("expansion/"+expansion)

    def loadTree(self, filename=None):
        tree = None
        if filename:
            try:
                tree = et.parse(filename)
                root = tree.getroot()
                if root.tag == "expansion":
                    items = root.find("items")
                    if items is not None:
                        tree = et.ElementTree(items)
                    else:
                        tree = None
            except (FileNotFoundError, et.ParseError) as e:
                print(str(e))
        return tree

    def addToTree(self, filename=None):
        """ Adding another set of skills to the skill tree

        Args:
            filename (str): the file to parse
        """

        if filename is None:
            return

        local_tree = self.loadTree(filename)
        if local_tree is None:
            return

        items = local_tree.findall(".//item")
        groups = self.xml_items.findall(".//group")
        for item in items:
            name = item.get("name")
            existing_item = self.getItem(name)
            if existing_item is None:
                parent = item.get("parent", "0")
                relevant_group = None
                for group in groups:
                    id = group.get("id", "")
                    if parent == id:
                        relevant_group = group
                        break
                relevant_group.append(item)

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
        skill = self.xml_items.find(".//item[@name='"+name+"']")
        return skill

