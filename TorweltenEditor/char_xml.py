"""
This module is used to store, access and modify a
characters ElementTree representation
"""

import xml.etree.ElementTree as et
import tkinter as tk
import random
from datetime import datetime
import config

msg = config.Messages()
cd = config.CharData()

class Character(object):
    """ a character object 

    this is mainly a wrapper around the underlying ElementTree which 
    allows easy access to the appropriate parts of the tree ...

    """

    def __init__(self):
        # this is the xml interpretation of the character
        self.ATTRIB_LIST = [
            cd.PHY,
            cd.MEN,
            cd.SOZ,
            cd.NK,
            cd.FK,
            cd.LP,
            cd.EP,
            cd.MP
        ]

        # this is the main ElementTree!
        self.xml_char = self._newChar()

        # initial event
        self.logEvent(self.xml_char.getroot(), op=cd.CREATED)

        # some of the data is needed in other variables as well
        # the charactere attributes are stored as tkinter IntVar in a dict
        self.attrib_values = {}
        self.attrib_trace = {}

        self.skill_values = {}
        self.skill_trace = {}

        self.data_values = {}
        self.data_trace = {}
        
        self.xp_avail = tk.IntVar()

        self.account_balance = tk.StringVar()
        self.updateAccount(0)
        # this variable holds temporary xp costs for increasing skills
        self.xp_cost = {}

        self.items = {}

        self.widgets = {}
    
    # create a character
    def _newChar(self):
        """ create a new character element tree

         Returns:
            et.ElementTree: the character skeleton
        """

        char = et.Element('character')
        basics = et.SubElement(char, 'basics')
        et.SubElement(basics, 'xp', total='0', available='0')
        et.SubElement(basics, 'edit', type='generation')
        attributes = et.SubElement(char, 'attributes')
        for attr in self.ATTRIB_LIST:
            et.SubElement(attributes, 'attribute', name=attr, value='0')
        et.SubElement(char, 'traits')
        et.SubElement(char, 'skills') 
        inventory = et.SubElement(char, 'inventory')
        et.SubElement(inventory, "account", name="0")
        et.SubElement(char, 'contacts')
        et.SubElement(char, 'events')
        char_tree = et.ElementTree(char)
        return char_tree

    def load(self, filename):
        """ loading a character from disk

        Args:
            filename (string): a filename to load from.
        """

        result = -1

        with open(filename, mode="rb") as file:
            result = 0
            try:
                self.xml_char = et.parse(file)
            except et.ParseError:
                return 1
            root = self.xml_char.getroot()
            if root.tag != "character":
                self.xml_char = self._newChar()
                return 2
            self.logEvent(self.xml_char.getroot(), op=cd.LOADED)

        return result

    def save(self, filename):
        """ Saving a character to an XML file

        Args:
            filename (string): a filename to save to.
        """

        with open(filename, mode="wb") as file:
            self.logEvent(self.xml_char.getroot(), op=cd.SAVED)
            self.xml_char.write(file, encoding="utf-8", xml_declaration=True)

    def addXP(self, amount, reason=None):
        """ Adding experience points to character

         Args:
            amount (int): how many XP to add
                This can be negative.
            reason (str): a reason for that modification
                Will be used in the eventlog
        """

        xp = self.xml_char.find('basics/xp')
        total_xp = int(xp.get('total')) + amount
        xp.set("total", str(total_xp))
        self.updateAvailableXP(amount)
        self.logEvent(xp, mod=amount, op=reason)

    def getEditMode(self):
        """ Retrieve the edit mode the character is currenty in

        Returns:
            str: edit mode
        """

        edit_type = self.xml_char.find('basics/edit')
        return edit_type.get('type')

    def getFreeMoney(self):
        """ Retrieve the free money flag
                
        Returns:
            (str) "true" or None
        """

        edit_type = self.xml_char.find('basics/edit')
        return edit_type.get('free_money')

    def getFreeXP(self):
        """ Retrieve the free xp flag 
        
        Returns:
            (str) "true" or None
        """

        edit_type = self.xml_char.find('basics/edit')
        return edit_type.get('free_xp')

    def setEditMode(self, edit_mode, free_xp=None, free_money=None):
        """ Setting the characters edit mode

        edit_mode (str): "generation", "edit", "simulation", "view"
        """

        ALLOWED_MODES = [cd.GENERATION, cd.EDIT, cd.VIEW, cd.SIMULATION]
        if edit_mode in ALLOWED_MODES:
            edit_type = self.xml_char.find('basics/edit')

            if edit_type.get("type") != edit_mode:
                edit_type.set("type", edit_mode)

                self.logEvent(
                    edit_type,
                    mod=edit_mode,
                    op=cd.SWITCHED_EDIT_MODE
                )

            if free_xp:
                if edit_type.get("free_xp") != "true":
                    self.logEvent(
                        edit_type,
                        mod="on",
                        op=cd.SWITCHED_XP_MODE
                    )

                edit_type.set("free_xp", "true")
            else:
                try:
                    del edit_type.attrib["free_xp"]
                    self.logEvent(
                        edit_type,
                        mod="off",
                        op=cd.SWITCHED_XP_MODE
                    )
                except KeyError:
                    pass

            if free_money:
                if edit_type.get("free_money") != "true":
                    self.logEvent(
                        edit_type,
                        mod="on",
                        op=cd.SWITCHED_MONEY_MODE
                    )

                edit_type.set("free_money", "true")
            else:
                try:
                    del edit_type.attrib["free_money"]
                    self.logEvent(
                        edit_type,
                        mod="off",
                        op=cd.SWITCHED_MONEY_MODE
                    )
                except KeyError:
                    pass

    # get a single attribute value # #
    def getAttributeValue(self, name):
        """ Retrieves the value of a given attribute

        Args:
            name (str): one of the attribute acronyms
        Returns:
            int: value of given attribute
        """

        if name in self.ATTRIB_LIST:
            search = "attributes/attribute[@name='"+name+"']"
            attr = self.xml_char.find(search)
            value = int(attr.get('value'))
            return value
        else:
            raise ValueError("Valid values"+str(self.ATTRIB_LIST))

    def getAvailableXP(self):
        """ Get the characters current available XP

        Returns:
            int: Available XP
        """

        xp_element = self.xml_char.find("basics/xp")
        return int(xp_element.get('available'))

    def addSkill(self, skill):
        """ Adding a skill to the character

        Args:
            skill (Element<skill>): The skill to add
        """

        if skill is not None:
            skill.set("value", "0")
            charskills = self.xml_char.find('skills')
            charskills.append(skill)
            self.logEvent(skill, op=cd.ADDED)

    def delSkill(self, name):
        """ Removing a skill from a character

        Args:
            name (str): The name of the skill to remove
        """

        skills = self.xml_char.find("skills")
        skill = self.xml_char.find("skills/skill[@name='"+name+"']")
        if skill is not None:
            value = int(skill.get("value"))
            skill_type = skill.get("type")
            xp = value * (value + 1)
            if skill_type == "language" or skill_type == "passive":
                xp /= 2
            self.updateAvailableXP(xp)
            self.logEvent(skill, op=cd.REMOVED)
            skills.remove(skill)
    
    def addTrait(self, full_trait, variables, xp_var, description=None):
        """ Adding a new trait to the character

        Args:
            full_trait (Element<trait): The full trait from the trait tree
            variables (dict{str:StingVars}): selected data
            xp_var (StringVar): containing the xp cost for the trait
            description (str): a descripion
        """

        # building the element skeleton
        trait = et.Element("trait")
        trait_id = self.getHighestTraitID() + 1
        trait.set("id", str(trait_id))
        xp = xp_var.get()
        xp = xp[1:-1]
        trait.set("xp", str(xp))
        trait_name = str(full_trait.get("name"))
        trait.set("name", trait_name)

        # get the specification
        specification = full_trait.find("specification")
        if specification is not None:
            spec_name = specification.get("name", "")
            spec_value = str(variables["spec"].get())
            spec = et.SubElement(trait, "specification")
            spec.set("name", spec_name)
            spec.set("value", spec_value)

        # get the ranks
        ranks = full_trait.findall("rank")
        if ranks:
            for rank in ranks:
                rank_id = rank.get("id")
                rank_name = rank.get("name")
                id_tag = "rank-"+rank_id
                rank_value = str(variables["rank_"+rank_id].get())
                rank_tag = et.SubElement(trait, "rank")
                rank_tag.set("name", rank_name)
                rank_tag.set("id", rank_id)
                rank_tag.set("value", rank_value)

        # get the variables
        variable_tags = full_trait.findall("variable")
        if variable_tags:
            for variable in variable_tags:
                var_id = variable.get("id")
                var_name = variable.get("name")
                var_value = str(variables["var_"+var_id].get())
                var_tag = et.SubElement(trait, "variable")
                var_tag.set("id", var_id)
                var_tag.set("name", var_name)
                var_tag.set("value", var_value)

        if len(description) <= 1:
            full_desc = full_trait.find("description")
            if full_desc is not None:
                text = full_desc.text
                if text:
                    description = text

        description_tag = et.SubElement(trait, "description")
        description_tag.text = description

        char_traits = self.xml_char.find('traits')
        char_traits.append(trait)
        self.updateAvailableXP(-int(xp))
        
        self.logEvent(trait, op=cd.ADDED, mod=trait_name)

    def resetTraitIDs(self):
        """ Reset trait ids if necessary """

        traits = self.getTraits()
        trait_id = 0
        for trait in traits:
            trait.set("id", str(trait_id))
            trait_id += 1
    
    def getHighestTraitID(self):
        """ Retrieves the highest given trait ID

        Returns:
            int: highest assigned id
        """

        highest_id = 0
        traits = self.getTraits()
        id_list = [int(trait.get("id", "0")) for trait in traits]
        if id_list:
            highest_id = max(id_list)
        return highest_id

    def updateData(self, data_name, data_value):
        """ Updating basic character data like name or species

        Args:
            data_name (str): the name of the data element
            data_value (str): the value associated with that name
        """

        basics = self.xml_char.find("basics")
        dataset = basics.find("./data[@name='"+data_name+"']")
        if dataset is not None:
            cur_value = dataset.get("value")
            if data_value != cur_value:
                dataset.set("value", str(data_value))
                self.logEvent(dataset, op=cd.UPDATED, mod=cur_value)
        elif data_value != "":
            dataset = et.Element("data")
            dataset.set("name", str(data_name))
            dataset.set("value", str(data_value))
            basics.append(dataset)
            self.logEvent(dataset, op=cd.ADDED)

    def getData(self, data_name):
        """ Retrieve basic data about the character

        Args:
            data_name (str): the name of the data to get

        Returns:
            str: The searched information or an empty string
        """

        data_value = ""
        dataset = self.xml_char.find(".basics/data[@name='"+data_name+"']")
        if dataset is not None:
            data_value = dataset.get("value")
        return data_value

    def skillChange(self, var_name, e=None, m=None):
        """ Handle a skill change via spinbox input

        this is bound as .trace() to the spinbox

        Args:
            var_name (string): the tk.IntVar we are tracing
            e (unused): given by .trace()
            m (unused): given by .trace()
        """

        skill_name = self.skill_trace[var_name]
        xml_skill = self.getSkill(skill_name)
        old_value = int(xml_skill.get("value"))
        new_value = old_value

        # we have to make sure a number is given
        # and it is within the bounds of a skill
        try:
            new_value = self.skill_values[skill_name].get()
            if new_value > 3:
                new_value = 3
                self.skill_values[skill_name].set(new_value)
            if new_value < 0:
                new_value = 0
                self.skill_values[skill_name].set(new_value)
        except ValueError:
            self.skill_values[skill_name].set(old_value)

        # passive skills are at half cost ...
        skill_type = xml_skill.get("type")
        modify = 1
        if skill_type == "passive" or skill_type == "language":
            modify = 2

        if new_value != old_value:
            old_xp_cost = (old_value * (old_value + 1)) / modify
            new_xp_cost = (new_value * (new_value + 1)) / modify
            xp_cost = new_xp_cost - old_xp_cost
            self.updateAvailableXP(-xp_cost)
            xml_skill.set("value", str(new_value))
            self.logEvent(xml_skill, op=cd.UPDATED)

    def increaseAttribute(self, attr):
        """ Incremental increase of an attribute

        Note:
            used in edit mode

        Args:
            attr: the acronym of the modified attribute
        """

        if attr not in self.ATTRIB_LIST:
            raise ValueError("attr must be one of: "+str(self.ATTRIB_LIST))

        old_value = self.getAttributeValue(attr)
        new_value = old_value + 1
        # limit to 9
        if new_value > 9:
            new_value = 9
        old_xp = old_value * (old_value + 1)
        new_xp = new_value * (new_value + 1)
        xp_cost = new_xp - old_xp
        xp_avail = self.xp_avail.get()
        
        # only increase if there is enough xp available
        if xp_avail >= xp_cost > 0:
            self.setAttribute(attr, str(new_value))
            self.updateAvailableXP(-xp_cost)

    def increaseSkill(self, skill_name):
        """ Incremental increase of a skill

        Note:
            used in edit mode

        Args:
            skill_name (str): name of the skill to change
        """

        search = ".//skill[@name='"+skill_name+"']"
        xml_skill = self.xml_char.find(search)
        old_value = int(xml_skill.get("value"))
        new_value = old_value + 1

        # limit for skills is 3
        if new_value > 3:
            new_value = 3
        old_xp = old_value * (old_value + 1)
        new_xp = new_value * (new_value + 1)
        xp_cost = new_xp - old_xp

        # half cost for passive skills
        skill_type = xml_skill.get("type")
        modifier = 1
        if skill_type == "passive" or skill_type == "language":
            modifier = 0.5
        
        xp_cost *= modifier
        xp_avail = self.xp_avail.get()

        # only increase if there is enough xp available
        if xp_avail >= xp_cost > 0:
            self.updateAvailableXP(-xp_cost)
            self.skill_values[skill_name].set(new_value)
            xml_skill.set("value", str(new_value))
            self.logEvent(xml_skill, op=cd.UPDATED)

    def sortSkills(self):
        """ Sorting skills by id"""

        skills = self.xml_char.find("skills")
        skill_list = []
        for skill in skills:
            key = skill.get("id")
            name = skill.get("name")
            skill_list.append((key, name, skill))
        skill_list.sort()
        # overwriting the skills ... 
        skills[:] = [new_skill[-1] for new_skill in skill_list]

    def attributeChange(self, var_name, e=None, m=None):
        """ Handle an attribute change via Spinbox input

        varname (string): the tk.IntVar we are tracing
        e (unused): given by .trace()
        m (unused): not used (given by .trace())
        """

        attrib_name = self.attrib_trace[var_name]
        old_value = self.getAttributeValue(attrib_name)
        new_value = old_value
            
        # try reading the IntVar and make sure it is 
        # within the valid bounds. 
        try:
            new_value = self.attrib_values[attrib_name].get()
            if new_value > 9:
                new_value = 9
                self.attrib_values[attrib_name].set(new_value)
            if new_value < 0:
                new_value = 0
                self.attrib_values[attrib_name].set(new_value)
        except ValueError:
            self.attrib_values[attrib_name].set(old_value)

        # calculate xp cost and update attribute and xp. 
        old_xp_cost = old_value * (old_value + 1)
        new_xp_cost = new_value * (new_value + 1)
        xp_cost = new_xp_cost - old_xp_cost
        self.updateAvailableXP(-xp_cost)
        self.setAttribute(attrib_name, new_value)

    def setAttribute(self, attr, value):
        """ setting the attribute

        Note:
            This will not update the XP

        Args:
            attr (str): the acronym of the attribute to change
            value (str): the new value to set the attribute to
        """

        if attr not in self.ATTRIB_LIST:
            raise ValueError("attr must be from: "+str(self.ATTRIB_LIST))

        search = "attributes/attribute[@name='"+attr+"']"
        xml_attr = self.xml_char.find(search)
        xml_attr.set("value", str(value))
        self.attrib_values[attr].set(value)
        self.logEvent(xml_attr, op=cd.UPDATED)

    def getTraits(self):
        """ Retrieving the characters traits

        Returns:
            [Element<trait>,...]: the traits
        """

        xml_traits = self.xml_char.findall("traits/trait")
        return xml_traits

    def getTrait(self, name):
        """ Retrieve a single character trait by name

        Attr:
            name (str): Name of the trait

        Returns:
             Element<trait>: a single trait Element
                None: if not existing
        """

        search = "traits/trait[@name='"+name+"']"
        xml_trait = self.xml_char.find(search)
        return xml_trait

    def getTraitByID(self, id):
        """ Retrieve a single character trait by its id

        Attr:
            id(int):

        Returns:
             Element<trait>: a single trait Element
                None: if not existing
        """

        id = str(id)
        search = "traits/trait[@id='"+id+"']"
        xml_trait = self.xml_char.find(search)
        return xml_trait

    def removeTraitByID(self, id):
        """ Removing a trait based on its id

        Attr:
            id(int):

        """

        id = str(id)
        traits = self.xml_char.find("traits")
        trait = traits.find("trait[@id='"+id+"']")
        xp = int(trait.get("xp"))
        if trait is not None:
            self.logEvent(trait, op=cd.REMOVED)
            traits.remove(trait)
            self.updateAvailableXP(xp)

    def updateTraitById(self, id, xp=None, description=None):
        traits = self.xml_char.find("traits")
        trait = traits.find("trait[@id='" + id + "']")

        if xp:
            cur_trait_xp = int(trait.get("xp"))
            trait.set("xp", str(cur_trait_xp + xp))
            self.updateAvailableXP(-xp)





    def getSkills(self):
        """ Get all character skill elements

        Returns:
            [Element<skill>,...]: List of skills
        """

        skills = self.xml_char.findall("skills/skill")
        return skills

    def getSkill(self, skill_name):
        """ Get a single skill by name

        Args:
            skill_name (str): name of the searched skill

        Returns:
            Element<skill>: the skills element
        """

        search = "skills/skill[@name='"+skill_name+"']"
        xml_skill = self.xml_char.find(search)
        return xml_skill

    def getSkillById(self, id):
        """ Get a single skill by name

            Args:
                id (int): skill id

            Returns:

                Element<skill>: the skills element
            """

        id = str(id)
        search = "skills/skill[@id='"+id+"']"
        skill = self.xml_char.find(search)
        return skill

    def getTotalXP(self):
        """ Retrieve the current total experience

        Returns:
            int: total XP
        """

        xp_element = self.xml_char.find("basics/xp")
        return int(xp_element.get('total'))

    def updateAvailableXP(self, value):
        """ Updates the available experience points

        Note:
            the given value is added to the current value

        Args:
            value (int): the experience to add/remove
        """
        xp_element = self.xml_char.find("basics/xp")
        value = int(value)
        if self.getFreeXP():
            value = "X"
        else:
            old_value = int(float(xp_element.get('available')))
            new_value = int(old_value + value)
            xp_element.set("available", str(new_value))
            self.xp_avail.set(new_value)
        self.logEvent(xp_element, mod=value, op=cd.UPDATED)

    def getInventory(self):
        """ Retrieve the characters inverntory

        Returns:
            Element<inventory>: The complete inventory of a character
        """

        return self.xml_char.find("./inventory")

    def getItems(self, name=None, item_type=None):
        """ This retrieves a (filtered) item list

        Args:
            name (str): [Optional] return only items with that name
            item_type(str): [Optional] return only items from that item type.
            
        Returns:
            [Element<item>,...]: (filtered) item list
        """

        inventory = self.getInventory()
        items = None
        name_filter = ""
        type_filter = ""
        if name:
            name_filter = "[@name='"+name+"']"
        if item_type:
            type_filter = "[@type='"+item_type+"']"
        search = "./item"+name_filter+type_filter
        return inventory.findall(search)

    def getItemById(self, id):
        """ Retrieve an item based on its id

        Args:
            id (int): item id
            
        Returns:
            Element<item>: an item element
        """

        id = str(id)        
        inventory = self.getInventory()
        item = inventory.find("item[@id='"+id+"']")
        return item

    def addItem(self, item, account="0"):
        """ Adding an item to the characters inventory
        
        item (Element<item>): an item element
        account (str): the name of the account from which to pay
        """

        item_price = float(item.get("price"))
        item_quantity = int(item.get("quantity"))
        price_per_unit = item_price / item_quantity
        item.set("price", str(price_per_unit))

        # does the character already own this?
        identical_item = self.getIdenticalItem(item)
        if identical_item is not None:
            old_quantity = int(identical_item.get("quantity"))
            item_quantity = int(item.get("quantity"))
            new_quantity = old_quantity + item_quantity
            identical_item.set("quantity", str(new_quantity))
            self.logEvent(
                identical_item,
                op=cd.ADDED,
                mod=item.get("quantity")
            )
        else:
            new_id = self.getHighestItemID() + 1
            item.set("id", str(new_id))
            inventory = self.getInventory()
            inventory.append(item)
            self.logEvent(
                item,
                op=cd.ADDED,
                mod=item.get("quantity")
            )
        # pay for item
        self.updateAccount(
            -item_price,
            account,
            reason=msg.LOG_ACCOUNT_PAY_ITEM
        )
    
    def splitItemStack(self, item, amount):
        """ Splits an item stack

        Args:
            item (Element<item>): item stack to split
            amount (int): number of items to make into a new item stack
                number will be sanitized to
        Returns:
            (int,int): number of items left in the original itemstack,
                       id of the new item stack
        """

        amount = int(amount)

        item_quantity = int(item.get("quantity"))
        if item_quantity > 1:
            # limit the split to the stack size
            if amount > item_quantity:
                amount = item_quantity - 1
            if amount < 1:
                amount = 1

            inventory = self.getInventory()
            
            new_item = et.Element("item")
            for attrib in item.attrib:
                new_item.set(attrib, item.attrib[attrib])
            for tag in item:
                new_item.append(tag)
            new_id = self.getHighestItemID() + 1
            new_item.set("id", str(new_id))
            inventory.append(new_item)

            # set quantities
            new_item.set("quantity", str(amount))
            item_quantity -= amount
            item.set("quantity", str(item_quantity))

            self.logEvent(new_item, op=cd.ITEM_SPLIT)
            self.logEvent(item)  # for integrity reasons
            self.unpackItem(new_item)
            return item_quantity, new_id

    def condenseItem(self, item):
        """ condense all identical items into one
        
        Args:
            item (Element<item>): an item stack
        Returns: 
            int: final quantity of that item
        """
        item_quantity = int(item.get("quantity"))
        identical_item = self.getIdenticalItem(item)
        inventory = self.getInventory()
        while identical_item is not None:
            # add the quantity of the other item to this item
            # and remove the other item
            identical_quantity = int(identical_item.get("quantity"))
            item_quantity += identical_quantity
            item.set("quantity", str(item_quantity))
            inventory.remove(identical_item)
            identical_item = self.getIdenticalItem(item)
            self.logEvent(item, op=cd.ITEM_CONDENSED)
        return item_quantity

    def setItemQuantity(self, item, quantity):
        """ you can set the item quantity to any number ...
        Args:
            item (et.Element<item>): the item to modify
            quantity (int): the value to set the quantity to
                (a value <= 0 will remove the item)
        """
        
        if quantity > 0:
            item.set("quantity", str(quantity))
        else:
            inventory = self.getInventory()
            inventory.remove(item) 

    def setActiveChamber(self, weapon, chamber=1):
        """ Setting the active chamber of a weapon

        Note:
            This is intended for multi-chambered weapons
            like revolvers

        Args:
            weapon (Element<item>): A weapon item
            chamber (int): the chamber to set as active
            chamber (str): "next", "random"
        """

        ammo_tag = weapon.find("ammo")
        if ammo_tag is not None:
            chambers = int(ammo_tag.get("chambers", "1"))

            actions = ["next", "random"]
            if type(chamber) == str and chamber not in actions:
                try:
                    chamber = int(chamber)
                except ValueError as e:
                    print(e)
                    pass

            if chamber == "next":
                current = int(ammo_tag.get("active", "1"))
                chamber = current + 1
                if chamber > chambers:
                    chamber = 1
                ammo_tag.set("active", str(chamber))
            elif chamber == "random":
                chamber = random.randint(1, chambers)
                ammo_tag.set("active", str(chamber))
            elif 1 <= chamber <= chambers:
                ammo_tag.set("active", str(chamber))

            self.logEvent(weapon, op=cd.ITEM_ROTATECHAMBER)
            return chamber

    @staticmethod
    def getActiveChamber(weapon):
        """ Get the selected chamber of a weapon

        Returns:
            int: active chamber
        """
        ammo_tag = weapon.find("ammo")
        active = None
        if ammo_tag is not None:
            active = int(ammo_tag.get("active", "1"))
        return active

    def getRoundFromChamber(self, weapon, chamber):
        """ get the bullet in a specific chamber

        Note:
            if asked chamber does not exist
             the bullet for chamber 1 is returned

        Args:
            weapon (Element<item): the weapon to check for ammo
            chamber (int): the chamber to look in

        Return:
            Element<item>: the loaded bullet
        """

        ammo_tag = weapon.find("ammo")
        bullet = None
        if ammo_tag is not None:
            chambers = int(ammo_tag.get("chambers", "1"))
            chamber = int(chamber)
            if chamber < 1 or chamber > chambers:
                chamber = 1
            ammo_list = ammo_tag.get("loaded", "x").split()
            if ammo_list[0] != "x":
                round_id = ammo_list[chamber - 1]
                bullet = self.getItemById(round_id)
        return bullet

    def reloadChamber(self, ammo, weapon):
        """ Reload chamber with new bullet

        Note:
            The current loaded bullet will be returned
            to the characters inventory

        Args:
            ammo (Element<item>): the new bullet
            weapon (Element<item>): the weapon
        """
        
        ammo_tag = weapon.find("ammo")
        content = ammo_tag.get("loaded", "-1")
        if content != "-1":
            loaded = self.getItemById(int(content))
            if loaded is not None:
                self.unpackItem(loaded)

        ammo_id = "-1"
        if ammo is not None:
            quantity = int(ammo.get("quantity"))
            ammo_id = int(ammo.get("id"))
            if quantity > 1:
                rest, ammo_id = self.splitItemStack(ammo, 1)
                ammo = self.getItemById(ammo_id)

            self.unpackItem(ammo)
            self.packItem(ammo, weapon)
        ammo_tag.set("loaded", str(ammo_id))

        self.logEvent(weapon)  # for integrity reasons

    def loadRoundInChamber(self, ammo, weapon):
        """ Loading the given round into the active chamber

        Args:
            ammo (Element<item>): The round to load
                if quantity > 1 item stack will be split
            weapon (etElement<item>): The weapon to load
                needs to have an <ammo> tag
        Returns:
            bool: True if successfully loaded
        """

        success = False
        ammo_tag = weapon.find("ammo")
        active_chamber = int(ammo_tag.get("active", "1"))
        loaded = ammo_tag.get("loaded", "-1")
        chambers = int(ammo_tag.get("chambers", "1"))
        loaded_list = loaded.split()
        while len(loaded_list) < chambers:
            loaded_list.append("-1")
        
        if loaded_list[active_chamber - 1] == "-1":
            if int(ammo.get("quantity")) > 1:
                item_quantity_and_new_item_id = self.splitItemStack(ammo, 1)
                new_id = item_quantity_and_new_item_id[1]
                ammo = self.getItemById(new_id)
            self.packItem(ammo, weapon)
            ammo_id = ammo.get("id", "-1")
            loaded_list[active_chamber - 1] = ammo_id
            loaded = " "
            loaded = loaded.join(loaded_list).strip()
            ammo_tag.set("loaded", loaded)

            success = True

            self.logEvent(ammo)
            self.logEvent(weapon)

        return success

    def loadRoundInClip(self, ammo, clip):
        """ Loading a single round into a clip

        Args:
            ammo (Element<item>): The bullet to load
            clip (Element<item>): The clip to place the bullet in

        Returns:
            bool: True if successful

        """

        success = False
        size = int(clip.find("container").get("size"))
        current_content = clip.get("content", "").split(" ")
        number_loaded = 0
        if current_content[0] != "":
            number_loaded = len(current_content)

        space = size - number_loaded

        if space >= 1:
            # split 1 from the stack and add it to the clip ...
            if int(ammo.get("quantity")) > 1:
                new_quantity, new_id = self.splitItemStack(ammo, 1)
                new_ammo = self.getItemById(new_id)
                self.packItem(new_ammo, clip)
                success = True
            else: 
                self.packItem(ammo, clip)
                success = True
        return success

    def getContainers(self, equipped=True):
        """ Get a list of all (equipped) containers

        Args:
            equipped (bool): default=True return only equipped containers

        Returns:
            [Element<item>,...]: list of items which all have a <container> tag
        """
        items = self.getItems()
        
        containers = []
        for item in items:
            container = item.find("container")
            if container is not None:
                if equipped and item.get("equipped", "0") == "1":
                    containers.append(item)
                elif not equipped:
                    containers.append(item)
        return containers

    def packItem(self, item, container):
        """ Places an item inside a container

        Note:
            As of now there is no check if an item possibly fits into the
            container, therefore it is possible to place for example a
            toolbox inside a shirt pocket.

        Args:
            item (Element<item>): The item to put into the container.
            container: (Element<item>): the container item
        """

        if item.get("inside", "-1") != "-1":
            self.unpackItem(item)

        container_id = container.get("id")
        item_id = item.get("id")
        if container_id != item_id:
            # appending the item_id to the container content attribute
            container_content = container.get("content", "")
            container_content = container_content + " " + item_id
            container_content = container_content.strip()
            
            container.set("content", container_content)

            # writing the container to the item and unequipping the item 
            item.set("inside", container_id)
            item.set("equipped", "0")

            self.logEvent(item, mod=container_id, op=cd.ITEM_PACKED)
            self.logEvent(container, op=cd.ITEM_BAG)

    def unpackItem(self, item, equip=False):
        """ Removing an item from its container

        Args:
            item (Element<item>): The item to unpack from a container
            equip(bool)=False: if True the item will be equipped
        """

        container_id = int(item.get("inside", "-1"))
        if container_id >= 0:
            item_id = item.get("id")
            container = self.getItemById(container_id)
            contents = container.get("content")
            content_ids = contents.split()

            new_content = " "
            content_ids = [id for id in content_ids if id != item_id]
            new_content = new_content.join(content_ids).strip()
            container.set("content", new_content)
           
            item.set("inside", "-1")
            self.logEvent(container, op=cd.ITEM_BAG)

        if equip:
            item.set("equipped", "1")
            self.logEvent(item, mod=container_id, op=cd.ITEM_EQUIP)
        else:
            self.logEvent(item, mod=container_id, op=cd.ITEM_UNPACKED)

    def getWeight(self, item):
        """ Retrieving the weight of an item and all packed sub items

        Args:
            item (Element<item>): the item to put on the scale

        Returns:
            int: weight in grams
        """

        weight = 0
        if item is not None:
            quantity = int(item.get("quantity", "0"))
            single_weight = int(item.get("weight", "0"))
            weight = single_weight * quantity
            content = item.get("content", "")
            content_list = content.split()
            for item_id in content_list:
                sub_item = self.getItemById(item_id)
                if sub_item is not None:
                    sub_quantity = int(sub_item.get("quantity", "1"))
                    sub_weight = int(sub_item.get("weight", "0")) * sub_quantity
                    weight += sub_weight

                    # expanding our iterator (if necessary)
                    sub_content = sub_item.get("content", "")
                    sub_content_list = sub_content.split()
                    for sub_id in sub_content_list:
                        content_list.append(str(sub_id))

        return weight

    def getIdenticalItem(self, item, exclude=None):
        """ Looking for an identical item in the inventory

        This will try to find an item that is so similar that it can
        be stacked onto the given item.

        Note:
            This check is not absolute there may be false positives if
            the user changes the items quiet a bit ...

        Args:
            item (Element<item>): the item we want to find siblings of
            exclude [str, ...]: list of item id,s

        Returns
            Element<item>: another item that is so similar, they
                can securly stacked into one item stack
                None: if not identical item is found.
        """
        if not exclude:
            exclude = []
        identical_item = None
        item_name = item.get("name")
        item_options = item.findall("option")
        item_quality = item.get("quality")
        item_id = item.get("id", "x")
        item_inside = item.get("inside", "-1")

        # items with content or equipped items can't be identical
        item_content = item.get("content", "")
        item_equipped = int(item.get("equipped", "0"))
        if item_content == "" and item_equipped == 0:

            current_items = self.getItems(item_name)
            for current_item in current_items:
                cur_id = current_item.get("id")
                # filter exclude list
                if cur_id in exclude:
                    continue
                # first layer of check:
                # compare quality and item location.
                # make sure it is not actually the same item!!
                cur_equipped = current_item.get("equipped", "0")
                cur_inside = current_item.get("inside", "-1")
                cur_quality = current_item.get("quality")
                if (int(cur_quality) == int(item_quality)
                    and int(cur_inside) == int(item_inside)
                    and int(cur_equipped) != 1
                    and cur_id != item_id
                ):
                    # next step - comparing item options
                    cur_options = current_item.findall("option")
                    for cur_option in cur_options:
                        for item_option in item_options:
                            # to next item on differences ...
                            if (item_option.get("name")
                                    == cur_option.get("name")
                                and item_option.get("value")
                                    != cur_option.get("value")
                            ):
                                continue
                # definitly different (or literally the same)
                else:
                    continue
                # this is probably another instance of this item ...
                # let's check the description
                cur_description = current_item.find("description")
                if cur_description is not None:
                    cur_description = cur_description.text
                new_description = item.find("description")
                if new_description is not None:
                    new_description = new_description.text
                if cur_description is None:
                    cur_description = " "
                if new_description is None:
                    new_description = " "
                # foreplay is done - check ...
                if cur_description != new_description:
                    continue
                # yes we are sure they are identical
                identical_item = current_item
                break
            
        return identical_item
    
    def equipItem(self, item):
        """ Equipping an item

        Note:
            At this point there is no check if the item is equippable!

        Args:
            item (Element<item>): the item to equip
        """

        item.set("equipped", "1")
        self.logEvent(item, op=cd.ITEM_EQUIP)

    def unequipItem(self, item):
        """ Unequipping an item

        Args:
            item (Element<item>): the item to unequip
        """

        item.set("equipped", "0")
        self.logEvent(item, op=cd.ITEM_UNEQUIP)

    def getHighestItemID(self):
        """ retrieving the highest current item id

        Returns:
            int: highest id
        """

        items = self.getItems()
        id = 0
        for item in items:
            item_id = int(item.get("id", "0"))
            if item_id > id:
                id = item_id
        return id

    def getAccounts(self):
        """ Getting all the characters accounts

        Returns
            [Element<account>,...]: list of accounts
        """

        return self.xml_char.findall(".//account")

    def getAccount(self, name="0"):
        """ find a specific account of the character

        Args:
            name (str)="0": name of the account

        Returns:
            Element<account>: the searched account
        """

        search = ".//account[@name='"+name+"']"
        return self.xml_char.find(search)

    def createAccount(self, name):
        """ Create a new named account

        Args:
            name (str): the name of the new account
        """

        account = self.getAccount(name)
        if account is None:
            account = et.Element("account", {"name", name})
            inventory = self.getInventory()
            inventory.append(account)

    def deleteAccount(self, name):
        """ Removing an account

        Note:
            Any funds on the given account will be transferred to account "0".
            Account "0" can't be deleted.

        Args:
            name (str): name of the account to delete.
        """

        if name != "0":
            account = self.getAccount(name)
            if account is not None:
                balance = self.getAccountBalance(name)
                self.updateAccount(-balance, name)
                self.updateAccount(balance)
                inventory = self.getInventory()
                inventory.remove(account)
        
    def getAccountBalance(self, name="0"):
        """ Get the current balance on an account

        Args:
            name (str)="0": the account to get the balance for

        Returns:
            float: account balance
        """

        account = self.getAccount(name)
        balance = float(account.get("balance", "0.0"))
        return balance

    def updateAccount(self, amount, name="0", reason=None):
        """ Updating the balance on a characters account

        Params:
            amount (float): the amount
            name (str): name of the account
            reason (str): reason for the transaction
        """

        account = self.getAccount(name)

        if self.getFreeMoney():
            amount = "X"
        else:
            cur_balance = float(account.get("balance", "0.0"))
            new_balance = float(cur_balance) + float(amount)
            account.set("balance", str(new_balance))

            self.updateAccountDisplay(amount)

        self.logEvent(account, mod=amount, op=reason)

    def updateAccountDisplay(self, amount):
        # retrieve the total balance variable
        total_balance = self.account_balance.get()
        total_balance = total_balance.replace(",", ".")
        if "." not in total_balance:
            total_balance = 0.0
        total_balance = float(total_balance)
        total_balance += float(amount)

        total_balance = str(total_balance)
        total_balance = total_balance.replace(".", ",")
        if "," in total_balance[-2:]:
            total_balance += "0"
        # update the account and log transaction
        self.account_balance.set(total_balance)

    def newContact(self, name=""):
        """ Creating a new contact

        Args:
            name (str): [Optional] the name of the contact

        Returns:
            int: id of the new contact
        """
        id = self.getHighestContactId() + 1

        contact = et.Element("contact")
        contact.set("id", str(id))
        contact.set("name", str(name))

        contacts = self.xml_char.find("contacts")
        contacts.append(contact)

        if name != "":
            self.logEvent(contact, mod="name")

        return id

    def getContactById(self, id):
        """ Retrieve a contact based on its id

        Args:
            id (int): The id of the contact you are looking for

        Returns:
            Element<contact>: the contact
            None: if not found.
        """
        id = str(id)
        search = "./contacts/contact[@id='"+id+"']"
        contact = self.xml_char.find(search)
        return contact

    def removeContactById(self, id):
        """ Removes a single contact by id

        Args:
            id (int): id of the contact
        """

        contacts = self.xml_char.find("contacts")
        if contacts is not None:
            id = str(id)
            contact = contacts.find("contact[@id='"+id+"']")
            if contact is not None:
                contacts.remove(contact)

    def getContacts(self):
        """ Get a list of all contacts

        Returns:
            [et.Element() <contact>, ...]: the characters contacts
        """

        contacts = self.xml_char.findall("./contacts/contact")
        return contacts

    def getHighestContactId(self):
        """ Get the highest current contact id

        Returns:
            int: id of some contact
        """

        contacts = self.xml_char.findall("contacts/contact")
        highest_id = 0
        for contact in contacts:
            id = int(contact.get("id", "0"))
            if id > highest_id:
                highest_id = id
        return highest_id

    def getNotes(self):
        notes = self.xml_char.find(".//notes")
        if notes is None:
            basics = self.xml_char.find("basics")
            notes = et.SubElement(basics, "notes")
        return notes

    def findNoteById(self, id):
        id = str(id)
        return self.xml_char.find(".//note[@id='"+id+"']")

    def getHighestNoteId(self):
        notes = self.getNotes()
        highest_id = 0
        for note in notes:
            id = int(note.get("id", "0"))
            if id > highest_id:
                highest_id = id
        return highest_id

    def addNote(self):
        notes = self.xml_char.find(".//notes")
        id = str(self.getHighestNoteId() + 1)
        note = et.SubElement(
            notes,
            "note",
            {"id": id}
        )

    def delNote(self, id):
        notes = self.xml_char.find(".//notes")
        note = notes.find("note[@id='"+id+"']")
        if note is not None:
            notes.remove(note)

    def setImage(self, filename):
        """ Setting the reference to a character image

        Args:
            filename (str): Should point to a valid .png or .jpg file
        """

        image = self.xml_char.find("./basics/image")
        if image is not None:
            image.set("name", filename)
        else:
            basics = self.xml_char.find("./basics")
            image = et.SubElement(basics, "image", {"file": filename})

    def getImage(self):
        """ Get the stored image reference.

        Returns:
            Element<image>: an element with the image and scaling information
            None: if not found.
        """

        return self.xml_char.find("./basics/image")

    def setImageSize(self, size, x, y, scale):
        """ setting selection information for a specific 'size'

        Note:
            Valid sizes are defined in config.Page

        Args:
            size (str): the module size the image is stored for
            x(float): percentage of the width were the upper left point is
            y(float): percentage of the width were the upper left point is
            scale(float): scaling percentage
        """

        image_tag = self.xml_char.find("./basics/image")
        size_tag = image_tag.find("size[@name='"+size+"']")
        if size_tag is None:
            et.SubElement(
                image_tag,
                "size",
                {"name": size,
                 "x": str(x),
                 "y": str(y),
                 "scale": str(scale)
                 }
                )
        else:
            size_tag.set("x", str(x))
            size_tag.set("y", str(y))
            size_tag.set("scale", str(scale))

    def removeImage(self):
        """ Removing an image reference """

        basics_tag = self.xml_char.find("./basics")
        image_tag = basics_tag.find("image")
        basics_tag.remove(image_tag)

    def getPDFTemplate(self):
        """ get the last used template """

        tag = self.xml_char.find("./basics/pdftemplate")
        filename = None
        if tag is not None:
            filename = tag.get("path")
        return filename

    def setPDFTemplate(self, path):
        """store the last used template """

        basics_tag = self.xml_char.find("./basics")
        template_tag = basics_tag.find("./pdftemplate")
        if template_tag is not None:
            template_tag.set("path", path)
        else:
            et.SubElement(basics_tag, "pdftemplate", {"path": path})

    def logEvent(self, tag, mod=None, op=None):
        """ Logging changes to the character within itself

        tag (Element<any>) the character tag that is edited
        mod (string) - a modification information 
        op (string) - operational information on the transaction
        """
        
        event = et.Element("event")
        date = datetime.now().strftime(msg.DATEFORMAT)
        event.set("date", date)
        event.set("element", tag.tag)

        if mod:
            event.set("mod", str(mod))
        if op:
            event.set("op", str(op))

        # adding additional information ...
        if tag.tag == "xp":
            if mod == "X":
                event.set("mod", "XXX")
                event.set("xp", tag.get("available"))
            elif mod > 0:
                event.set("mod", "+"+str(mod))
                event.set("xp", tag.get("available"))
        if tag.tag == "attribute":
            name = tag.get("name")
            value = tag.get("value")
            event.set("name", name)
            event.set("value", value)
        elif tag.tag == "skill":
            name = tag.get("name")
            value = tag.get("value")
            id = tag.get("id")
            event.set("id", id)
            event.set("name", name)
            event.set("value", value)
        elif tag.tag == "trait":
            name = tag.get("name")
            xp = tag.get("xp")
            if op == cd.REMOVED:
                xp = str(-int(xp))
            event.set("name", name)
            event.set("xp", xp)
        elif tag.tag == "data":
            name = tag.get("name")
            value = tag.get("value")
            event.set("name", name)
            event.set("value", value)
        elif tag.tag == "item":
            name = tag.get("name")
            id = tag.get("id")
            quantity = tag.get("quantity")
            event.set("name", name)
            event.set("id", id)
            event.set("quantity", quantity)
        elif tag.tag == "contact":
            if "name" in mod:
                event.set("oldname", op)
            if "location" in mod:
                location = tag.get("location")
                event.set("loc", location)
            if "competency" in mod:
                competency = tag.get("competency", "")
                level = tag.get("competencylevel", "")
                if competency != "" and level != "":
                    event.set("comp", competency+" "+level)
            if "loyality" in mod:
                loyality = tag.get("loyality", "")
                event.set("loy", loyality)
            if "frequency" in mod:
                frequency = tag.get("frequency", "")
                event.set("frq", frequency)
            if "description" in mod:
                desc = tag.find("description")
                if desc is not None and desc.text:
                    length = len(desc.text)
                    event.set("desc", str(length))
            id = tag.get("id")
            event.set("id", id)

        events = self.xml_char.find("events")
        if events is None:
            root = self.xml_char.getroot()
            events = et.SubElement(root, "events")
        events.append(event)

    def getEvents(self):
        """ Get the stored events

        Returns:
            Element<events>: the events root element
        """

        return self.xml_char.find("events")
