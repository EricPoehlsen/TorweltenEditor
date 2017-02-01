# coding=utf-8

"""
This module is used to store, access and modify a characters ElementTree representation 
"""

import xml.etree.ElementTree as et
import tkinter as tk
import random
import skill_xml
import trait_xml
import item_xml
from datetime import datetime
import config

msg = config.Messages()

class Character():
    def __init__(self):
        # this is the xml interpretation of the character
        self.ATTRIB_LIST = ["phy","men","soz","nk","fk","lp","ep","mp"]
        self.xml_char = self._newChar()
        self.addEvent(self.xml_char.getroot(),op=msg.CHAR_CREATED)

        self.window = 0

        # some of the data is needed in other variables as well
        # the charactere attributes are stored as tkinter IntVar in a dict
        self.attrib_values = {}
        self.attrib_trace = {}

        # making the available as vars # #
        self.data_values = {}
        self.data_trace = {}
        
        self.xp_avail = tk.IntVar()
        self.account_balance = tk.StringVar()
        self.updateAccount(0)
        # this variable holds temporary xp costs for increasing skills
        self.xp_cost = {}

        # keeping track of the skills
        self.skill_values = {}
        self.skill_trace = {}

        self.items = {}

        self.widgets = {}
    
    # create a new empty character # #
    # DO NOT CALL OUTSIDE OF THIS CLASS! # #
    def _newChar(self):
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
        et.SubElement(inventory,"account", name="0")
        et.SubElement(char, 'contacts')
        et.SubElement(char, 'events')
        char_tree = et.ElementTree(char)
        return char_tree

    # load an existing character # #
    def load(self,file):
        self.xml_char = et.parse(file)
        self.addEvent(self.xml_char.getroot(),op=msg.CHAR_LOADED)

    # save the current character # #
    def save(self,file):
        self.addEvent(self.xml_char.getroot(),op=msg.CHAR_SAVED)
        self.xml_char.write(file,encoding = "utf-8", xml_declaration=True)
        file.close()
        
    def addXP(self,amount,reason=None):
        xp = self.xml_char.find('basics/xp')
        available_xp = int(xp.get('available')) + amount
        total_xp = int(xp.get('total')) + amount
        
        xp.set("available",str(available_xp))
        xp.set("total",str(total_xp))
        self.xp_avail.set(available_xp)
        self.addEvent(xp,mod=amount,op=reason)        


    # check in which edit mode the character is
    def getEditMode(self):
        edit_type = self.xml_char.find('basics/edit')
        return edit_type.get('type')

    # set the edit type of the charakter
    def setEditMode(self,edit_mode):
        """
        type: STRING: "generation", "edit", "simulation", "view"
        """
        ALLOWED_MODES = ["generation", "edit", "simulation", "view"]
        if edit_mode in ALLOWED_MODES:
            edit_type = self.xml_char.find('basics/edit')
            edit_type.set("type",edit_mode)
            self.addEvent(edit_type, mod=edit_mode, op=msg.CHAR_SWITCHED_EDIT_MODE)

    # get a single attribute value # #
    def getAttributeValue(self,name):
        """
        retrieve an attribute value
        name: the name of an attribute
        return: integer value
        """
        search = "attributes/attribute[@name='"+name+"']"
        attr = self.xml_char.find(search)
        value = int(attr.get('value'))
        return value

    # returns the available XP from the XML object as integer
    def getAvailableXP(self):
        xp_element = self.xml_char.find("basics/xp")
        return int(xp_element.get('available'))
    # add a known skill based on its name

    def addSkill(self,name):
        skilltree = skill_xml.SkillTree()
        new_skill = skilltree.getSkill(name)
        if new_skill is not None:
            new_skill.set("value", "0")
            charskills = self.xml_char.find('skills')
            charskills.append(new_skill)
            self.addEvent(new_skill,op=msg.CHAR_SKILL_ADDED)

    # add a skill element 
    def addSkillElement(self,skill):
        if skill is not None:
            skill.set("value", "0")
            charskills = self.xml_char.find('skills')
            charskills.append(skill)
            self.addEvent(skill,op=msg.CHAR_SKILL_ADDED)

    # remove a skill from a charakter
    def delSkill(self,name):
        charskills = self.xml_char.find("skills")
        skill = self.xml_char.find("skills/skill[@name='"+name+"']")
        if skill is not None:
            value = int(skill.get("value"))
            type = skill.get("type")
            xp = value * (value + 1)
            if (type == "language" or type == "passive"): xp = xp / 2
            self.updateAvailableXP(xp)
            self.addEvent(skill,op=msg.CHAR_SKILL_REMOVED)
            charskills.remove(skill)
    
    
    #  add a selected trait
    def addTrait(self,full_trait,vars,xp_var,description):
        trait = et.Element("trait")
        # set ID
        id = self.getHighestTraitID() + 1
        trait.set("id",str(id))

        xp = xp_var.get()
        xp = xp[1:-1]
        trait.set("xp", str(xp))
        trait.set("name", str(full_trait.get("name")))
        selected = et.SubElement(trait,"selected")
        # get the specification 
        specification = full_trait.find("specification")
        if specification is not None:
            selected.set("spec", str(vars["spec"].get()))

        # get the ranks
        ranks = full_trait.findall("rank")
        if (ranks):
            for rank in ranks:
                id = rank.get("id")
                id_tag = "rank-"+id
                selected.set(id_tag, str(vars["rank_"+id].get()))
        
        # get the variables
        variables = full_trait.findall("variable")
        if (variables):
            for variable in variables:
                id = variable.get("id")
                id_tag = "id-"+id
                selected.set(id_tag, str(vars["var_"+id].get()))
        
        if len(description) > 1:
            description_tag = et.SubElement(trait,"description") 
            description_tag.text = description

        char_traits = self.xml_char.find('traits')
        char_traits.append(trait)
        self.updateAvailableXP(-int(xp))
        
        self.addEvent(trait,op=msg.CHAR_TRAIT_ADDED)


    # just in case something is wrong with the IDs 
    def resetTraitIDs(self):
        traits = self.getTraits()
        id = 0
        for trait in traits:
            trait.set("id",str(id))
            id = id + 1
    
    # get the highest current trait id    
    def getHighestTraitID(self):
        """
        fetches the highest given trait ID
        return: INT
        """
        traits = self.getTraits()
        id = 0
        for trait in traits:
            trait_id = trait.get("id","0")
            trait_id = int(trait_id)
            if trait_id > id: id = trait_id
        return id

        
    # update basic character data or insert it if it does not yet exist
    def updateData(self, data_name, data_value):
        """
        updating basic character data like name or species
        data_name: the name of the data element
        data_value: the value associated with that name
        """
        basics = self.xml_char.find("basics")
        dataset = basics.find("./data[@name='"+data_name+"']")
        if dataset is not None:
            cur_value = dataset.get("value")
            if data_value != cur_value:
                dataset.set("value", str(data_value))
                self.addEvent(dataset, op=msg.CHAR_DATA_UPDATED)
        elif data_value != "":
            dataset = et.Element("data")
            dataset.set("name", str(data_name))
            dataset.set("value", str(data_value))
            basics.append(dataset)
            self.addEvent(dataset, op=msg.CHAR_DATA_CREATED)

    # retrieve data from character
    def getData(self, data_name):
        data_value = ""
        dataset = self.xml_char.find(".basics/data[@name='"+data_name+"']")
        if dataset is not None:
            data_value = dataset.get("value")
        return data_value

    ### TODO REMOVE IF NOT NEEDED ... 
    """
    def updateSkills(self):
        for skill in self.skill_values:
            xml_skill = self.getSkill(skill)
            cur_value = int(xml_skill.get("value"))
            new_value = self.skill_values[skill].get()

            if cur_value != new_value:
                xml_skill.set("value", str(new_value))
                self.addEvent(xml_skill,op=msg.CHAR_SKILL_CHANGED)
    """


    # changing a skill when a skill spinner changed
    # handling an IntVar.trace()
    # var_name: tcl variable name
    # empty: would be an index
    # access_type: w / r - we only care for writes!

    def skillSpinner(self, var_name, empty, access_type):
        if (access_type == "w"):
            skill_name = self.skill_trace[var_name]
            xml_skill = self.getSkill(skill_name)
            old_value = int(xml_skill.get("value"))
            new_value = old_value

            # we have to make sure a number is given and it is within the bounds of a skill
            try:
                new_value = self.skill_values[skill_name].get()
                if (new_value > 3): 
                    new_value = 3
                    self.skill_values[skill_name].set(new_value)
                if (new_value < 0): 
                    new_value = 0
                    self.skill_values[skill_name].set(new_value)
            except ValueError:
                self.skill_values[skill_name].set(old_value)
            
            # passive skills are at half cost ...
            type = xml_skill.get("type")
            modify = 1
            if (type == "passive" or type == "language"): modify = 2

            if new_value != old_value:
                old_xp_cost = (old_value * (old_value + 1)) / modify
                new_xp_cost = (new_value * (new_value + 1)) / modify
                xp_cost = new_xp_cost - old_xp_cost
                self.updateAvailableXP(-xp_cost)
                xml_skill.set("value", str(new_value))
                self.addEvent(xml_skill,op=msg.CHAR_SKILL_CHANGED)

    # increasing an attribute by one - used in edit mode ...
    def increaseAttribute(self,attr):
        success = False
        old_value = self.getAttributeValue(attr)
        new_value = old_value + 1
        # limit to 9
        if (new_value > 9): new_value = 9
        old_xp = old_value * (old_value + 1)
        new_xp = new_value * (new_value + 1)
        xp_cost = new_xp - old_xp
        xp_avail = self.xp_avail.get()
        
        # only increase if there is enough xp available
        if ((xp_avail >= xp_cost) and (xp_cost > 0)):
            self.setAttribute(attr,new_value)
            self.updateAvailableXP(-xp_cost)
            success = True
        return success

    # increasing a skill by one - used in edit mode ...
    def increaseSkill(self,skill_name):
        success = False
        xml_skill = self.xml_char.find(".//skill[@name='"+skill_name+"']")
        old_value = int(xml_skill.get("value"))
        new_value = old_value + 1

        # limit for skills is 3
        if new_value > 3: new_value = 3
        old_xp = old_value * (old_value + 1)
        new_xp = new_value * (new_value + 1)
        xp_cost = new_xp - old_xp

        # half cost for passive skills
        type = xml_skill.get("type")
        modifier = 1
        if (type == "passive" or type == "language"):
            modifier = 2
        
        xp_cost = xp_cost / modifier
        xp_avail = self.xp_avail.get()

        # only increase if there is enough xp available
        if ((xp_avail >= xp_cost) and (xp_cost > 0)):
            self.updateAvailableXP(-xp_cost)
            self.skill_values[skill_name].set(new_value)
            xml_skill.set("value", str(new_value))
            self.addEvent(xml_skill,op=msg.CHAR_SKILL_CHANGED)
            success = True
        return success

    # sorting skills ...
    def sortSkills(self):
        skills = self.xml_char.find("skills")
        skill_list = []
        for skill in skills:
            key = skill.get("id")
            skill_list.append((key,skill))
        skill_list.sort()
        # overwriting the skills ... 
        skills[:] = [new_skill[-1] for new_skill in skill_list]

    # updating an attribute wenn the spinner changes
    # handling an IntVar.trace()
    # var_name: tcl variable name
    # empty: would be an index
    # access_type: w / r - we only care for writes!
    def attributeSpinner(self, var_name, empty, access_type):
        if (access_type == "w"):
            attrib_name = self.attrib_trace[var_name]
            old_value = self.getAttributeValue(attrib_name)
            new_value = old_value
            
            # we have to make sure a number is given and it is within the bounds of an attribute
            try:
                new_value = self.attrib_values[attrib_name].get()
                if (new_value > 9): 
                    new_value = 9
                    self.attrib_values[attrib_name].set(new_value)
                if (new_value < 0): 
                    new_value = 0
                    self.attrib_values[attrib_name].set(new_value)
            except ValueError:
                self.attrib_values[attrib_name].set(old_value)

            old_xp_cost = old_value * (old_value + 1)
            new_xp_cost = new_value * (new_value + 1)
            xp_cost = new_xp_cost - old_xp_cost
            self.updateAvailableXP(-xp_cost)
            self.setAttribute(attrib_name, new_value)

    # returns a list with the names of the skills the character has
    def getSkillList(self):
        skills = list()
        xml_skills = self.xml_char.findall("skills/skill")
        for skill in xml_skills:
            skills.append(skill.get("name"))
        return skills    

    # return a list with the characters traits
    def getTraits(self):
        xml_traits = self.xml_char.findall("traits/trait")
        return xml_traits

    # return a character trait
    def getTrait(self, name):
        xml_trait = self.xml_char.find("traits/trait[@name='"+name+"']")
        return xml_trait

    # return a character trait
    def getTraitByID(self, id):
        xml_trait = self.xml_char.find("traits/trait[@id='"+id+"']")
        return xml_trait

    def removeTraitByID(self, id):
        traits = self.xml_char.find("traits")
        xml_trait = traits.find("trait[@id='"+id+"']")
        xp = int(xml_trait.get("xp"))
        self.addEvent(xml_trait,op=msg.CHAR_TRAIT_REMOVED)
        traits.remove(xml_trait)
        self.updateAvailableXP(xp)

    # returns a list with the names of the traits the character has
    def getTraitList(self):
        traits = list()
        xml_traits = self.xml_char.findall("traits/trait")
        for trait in xml_traits:
            traits.append(trait.get("name"))
        return traits    


    # returns the skills as a list of etree elements
    def getSkills(self):
        skills = list()
        xml_skills = self.xml_char.findall("skills/skill")
        for skill in xml_skills:
            skills.append(skill)
        return skills    

    # returns a single skill element by name
    def getSkill(self, skill_name):
        xml_skill = self.xml_char.find("skills/skill[@name='"+skill_name+"']")
        return xml_skill

    # returns a single skill element by Id
    def getSkillById(self, id):
        xml_skill = self.xml_char.find("skills/skill[@id='"+id+"']")
        return xml_skill


    # returns the available XP from the XML object as integer
    def getTotalXP(self):
        xp_element = self.xml_char.find("basics/xp")
        return int(xp_element.get('total'))

    # update the available XP in the XML object
    # the 'value' is added!
    def updateAvailableXP(self, value):
        xp_element = self.xml_char.find("basics/xp")
        old_value = int(float(xp_element.get('available')))
        new_value = int(old_value + value)
        xp_element.set("available",str(new_value))
        self.xp_avail.set(new_value)

    # update the changed attributes 
    def updateAttributes(self):
        pass
    
    # changing an attribute 
    def updateAttribute(self, attr_name, amount):
        # get the current value from the XML dataset
        xml_attr = self.xml_char.find("attributes/attribute[@name='"+attr_name+"']")
        old_value = int(xml_attr.get('value'))        
        
        # check if value in the Entry-Field is a valid integer
        # change to zero if not
        try: 
            int(self.attribs[attr_name].get())
        except ValueError:
            self.attribs[attr_name].set("0")
        
        # the new value would be ...
        new_value = self.attribs[attr_name].get() + amount
        
        # ... but we need to check for bounds
        if (new_value > 10): new_value = 10
        if (new_value < 0): new_value = 0

        # let us check for the xp_cost
        xp_cost_old = old_value * (old_value + 1)
        xp_cost_new = new_value * (new_value + 1)
        xp_cost = xp_cost_new - xp_cost_old
        
        self.updateAvailableXP(-xp_cost)
        
        # update the Entry_Field and XML tree
        self.setAttribute(attr_name, new_value)

    def setAttribute(self, attrib_name, value):
        xml_attr = self.xml_char.find("attributes/attribute[@name='"+attrib_name+"']")
        xml_attr.set("value", str(value))
        self.attrib_values[attrib_name].set(value)
        self.addEvent(xml_attr, op=msg.CHAR_ATTRIBUTE_CHANGED)



###############HANDLING THE INVENTORY # ################


    # retrieve the inventory object of a character
    def getInventory(self):
        inventory = self.xml_char.find("./inventory")
        return inventory

    # retrieve items from the character
    def getItems(self,name = None,item_type = None):
        """
        Get Items from the character xml
        name = None: otherwise give a string to retrieve all items with that name ...
        return: List of Items
        """
        inventory = self.getInventory()
        items = None
        name_filter = ""
        type_filter = ""
        if name: name_filter = "[@name='"+name+"']"
        if item_type: type_finter =  "[@type='"+item_type+"']"
        return inventory.findall("./item"+name_filter+type_filter)

    # retrieve an item by its ID
    def getItemById(self,id):
        inventory = self.getInventory()
        item = inventory.find("item[@id='"+id+"']")
        return item

    # add an item to the inventory
    def addItem(self,item,account = "0"):
        
        # check if the character already owns this item ... 
        item_price = float(item.get("price"))
        item_quantity = int(item.get("quantity"))
        price_per_unit = item_price / item_quantity
        item.set("price",str(price_per_unit))

        # if this is just another instance of this item 
        # so we simply update the quantity ...
        existing_item = self.getIdenticalItem(item)            
        if existing_item is not None:
            old_quantity = int(existing_item.get("quantity"))
            item_quantity = int(item.get("quantity"))
            new_quantity = old_quantity + item_quantity
            existing_item.set("quantity",str(new_quantity))
            self.addEvent(existing_item,op=msg.CHAR_ITEM_ADDED)
        else:                                          
            # set the item id
            new_id = self.getHighestItemID() + 1
            item.set("id",str(new_id))
        
            # add item to inventory
            inventory = self.getInventory()
            inventory.append(item)
            self.addEvent(item,op=msg.CHAR_ITEM_ADDED)

        
        # pay for the item (it does not matter if we increased the quantity of one item
        # or created a new item ...
        self.updateAccount(-item_price,account)
    
    # splitting an item stack
    def splitItemStack(self,item,amount):
        """ splits an item stack
        item: an et.Element() <item>
        amount: int > 1 (the method will try its best to sanitize bad input)
        return: (int,int) - what is left of the original itemstack and the id of the new item
        """
        try:
            amount = int(amount)
        except ValueError: amount = 1

        item_quantity = int(item.get("quantity"))
        if item_quantity > 1:
            # limit the split to the stack size
            if amount > item_quantity: amount = item_quantity - 1
            if amount < 1: amount = 1

            inventory = self.getInventory()
            
            # create new item
            new_item = et.Element("item")
            
            # copy attributes
            for attrib in item.attrib:
                new_item.set(attrib,item.attrib[attrib])
            
            # copy tags
            for tag in item:
                new_item.append(tag)

            # set new id
            id = self.getHighestItemID() + 1
            new_item.set("id",str(id))
            
            # set quantities
            new_item.set("quantity",str(amount))
            
            item_quantity = item_quantity - amount
            item.set("quantity",str(item_quantity))

            self.addEvent(new_item, op=msg.CHAR_ITEM_SPLIT)
            # add the new_item to the inventory
            inventory.append(new_item)

            return (item_quantity, id)

    def condenseItem(self,item):
        """ condense all identical items into one <item>
        item: et.Element() <item>
        return: int final quantity of that item
        """
        
        # retrieve an identical item (if none exists nothing will happen ...)
        item_quantity = int(item.get("quantity"))
        existing_item = self.getIdenticalItem(item)
        inventory = self.getInventory()
        while existing_item is not None:
            # add the quantity of the other item to this item and remove the other item
            existing_quantity = int(existing_item.get("quantity"))
            item_quantity = item_quantity + existing_quantity
            item.set("quantity",str(item_quantity))
            inventory.remove(existing_item)
            existing_item = self.getIdenticalItem(item)
            self.addEvent(item,op=msg.CHAR_ITEM_CONDENSED)
        return item_quantity

    # set the item quantity
    def setItemQuantity(self,item,quantity):
        """ you can set the item quantity to any number ...
        item: et.Element() <item>
        quantity: int (a value <= 0 deletes the item)
        """
        
        if quantity > 0:
            item.set("quantity", str(quantity))

        else:
            inventory = self.getInventory()
            inventory.remove(item) 
    
    # set the active chamber of a weapon ...
    def setActiveChamber(self,weapon,value):
        """ This method sets the active chamber of a weapon (esp. Revolvers)

        """
        success = False
        ammo_tag = weapon.find("ammo")
        if ammo_tag is not None:
            chambers = int(ammo_tag.get("chambers","1"))
            try:
                number = int(value)
            except ValueError:
                number = 0
            if number >= 1 and number <= chambers:
                ammo_tag.set("active",str(number))
                success = True

            if value == "next":
                current = int(ammo_tag.get("active","1"))
                next = current + 1
                if next > chambers: next = 1
                ammo_tag.set("active",str(next))
                success = True

            if value == "random":
                random_chamber = random.randint(1,chambers)
                ammo_tag.set("active",str(random_chamber))
                success = True

            self.addEvent(weapon,op=msg.CHAR_ITEM_ROTATECHAMBER)
            return success

    # get the active chamber of a weapon
    def getActiveChamber(self,weapon):
        ammo_tag = weapon.find("ammo")
        active = None
        if ammo_tag is not None:
            active = int(ammo_tag.get("active","1"))
        return active

    # gets the item loaded in a specific chamber
    def getRoundFromChamber(self,weapon,chamber):
        ammo_tag = weapon.find("ammo")
        round = None
        if ammo_tag is not None:
            chambers = int(ammo_tag.get("chambers","1"))
            chamber = int(chamber)
            if chamber < 1 or chamber > chambers:
                chamber = 1
            ammo_list = ammo_tag.get("loaded","x").split()
            if ammo_list[0] != "x":
                round_id = ammo_list[chamber - 1]
                round = self.getItemById(round_id)
        return round

    def reloadChamber(self,ammo,weapon):
        # get the status from the weapon
        
        ammo_tag = weapon.find("ammo")
        content = ammo_tag.get("loaded","-1")
        if content != "-1":
            loaded = self.getItemById(str(content))
            if loaded is not None:
                self.unpackItem(loaded)
        
        if ammo is not None: 
            ammo_id = ammo.get("id")
            self.unpackItem(ammo)
            self.packItem(ammo,weapon)
        else:
            ammo_id = "-1"
        ammo_tag.set("loaded",ammo_id)

    def removeRoundFromChamber(self,weapon,chamber=1):
        """ this method is used to remove a loaded round from the chamber
        weapon: et.Element() <item> needs <ammo> tag
        chamber: int - number of affected chamber (input is mildly sanitized)
        return: 0 - no round was chambered 
                1 - chambered round removed
        """
        result = 0
        # get the data ...
        ammo_tag = weapon.find("ammo")
        if ammo_tag is not None:
            loaded = ammo_tag.get("loaded","x")
            chambers = int(ammo_tag.get("chambers","1"))
            if loaded == "x":
                loaded_list = []
                i = 0
                while i < chambers:
                    loaded_list.append("-1")
                    i = i + 1
            else: loaded_list = loaded.split()

            # remove the round, if one is currently chambered
            if int(chamber) > chambers or int(chamber) < 1: 
                chamber = 1
                result = result + 10
            loaded_item = self.getItemById(loaded_list[chamber - 1])
            if loaded_item is not None: 
                self.unpackItem(loaded_item)
                result = result + 1
            loaded_list[chamber - 1] = "-1"
            new_content = ""
            i = 0
            for entry in loaded_list: 
                new_content = new_content + " " + loaded_list[i]
                i = i + 1
            new_content.strip()
            ammo_tag.set("loaded",new_content)
            ammo_tag.set("active",str(chamber))
        else: result = -1
        return result

    # loading a round into the chamber of a weapon
    def loadRoundInChamber(self,ammo,weapon):
        """ if this method is called the given item is loaded into the
        active chamber of the weapon
        ammo: etElement() <item> - if the quantity > 1 it will be split
        weapon: etElement() <item> - needs to have a <ammo> tag
        return: True if successful
        """
        success = False

        id = ammo.get("id")
        
        # get the status from the weapon
        ammo_tag = weapon.find("ammo")
        active_chamber = int(ammo_tag.get("active","1"))
        loaded = ammo_tag.get("loaded","-1")
        chambers = int(ammo_tag.get("chambers","1"))
        loaded_list = loaded.split()
        while len(loaded_list) < chambers:
            loaded_list.append("-1")
        
        # there can only be one bullet in a chamber
        if loaded_list[active_chamber - 1] == "-1":
            # split the ammo item if necessary
            if int(ammo.get("quantity")) > 1:
                item_quantity_and_new_item_id = self.splitItemStack(ammo,1)
                new_id = item_quantity_and_new_item_id[1]
                new_ammo = self.getItemById(str(new_id))
                self.packItem(new_ammo, weapon)
                id = new_id
            else: 
                self.packItem(ammo, weapon)

            # place the bullet
            loaded_list[active_chamber - 1] = str(id)
            loaded = ""
            for entry in loaded_list:
                loaded = loaded + " " + str(entry)
            loaded = loaded.strip()
            ammo_tag.set("loaded",loaded)
            success = True
        return success

    # loading a single round to a clip ...
    def loadRoundInClip(self,ammo,clip):
        success = False
        size = int(clip.find("container").get("size"))
        current_content = clip.get("content","").split(" ")
        number_loaded = 0
        if current_content[0] != "":
            number_loaded = len(current_content)

        space = size - number_loaded

        if space >= 1:
            # split 1 from the stack and add it to the clip ...
            if int(ammo.get("quantity")) > 1:
                item_quantity_and_new_item_id = self.splitItemStack(ammo,1)
                new_id = item_quantity_and_new_item_id[1]
                new_ammo = self.getItemById(str(new_id))
                self.packItem(new_ammo, clip)
            else: 
                self.packItem(ammo,clip)
            success = True
        return success


    # get all (equipped) containers
    def getContainers(self,equipped = True):
        """ get a list of all bags
        equipped=True: if False ALL bags will be returned, standard is 'only equipped bags'
        returns: [containers] a list of et.Element() <item> with a child <bag>
        """
        items = self.getItems()
        
        containers = []
        for item in items:
            container = item.find("container")
            if container is not None:
                if (equipped == True and item.get("equipped","0") == "1"):
                    containers.append(item)
                elif equipped == False:
                    containers.append(item)
        return containers

    # adding an item to a container
    def packItem(self,item,container):
        """ Putting an item into a container
        item: et.Element <item>  - the item to put into the container.
        container: et.Element <item> - the container item 
        Be aware: this method will not check if the item can be put into that container
        """
        
        # remove item from its current bag ...
        container_id = container.get("id")
        item_id = item.get("id")
        # making sure you don't pack an item into itself ...
        if container_id != item_id:
            # appending the item_id to the container content attribute
            container_content = container.get("content","")
            container_content = container_content + " " + item_id
            container_content = container_content.strip()
            
            container.set("content",container_content)

            # writing the container to the item and unequipping the item 
            item.set("inside",container_id)
            item.set("equipped","0")

            self.addEvent(item,op=msg.CHAR_ITEM_PACKED)
            self.addEvent(container,op=msg.CHAR_ITEM_PACKED_BAG)

    # removing an item from a container
    def unpackItem(self,item,equip=False):
        """ remove an item from the bag it is in ...
        We do not have to know which bag the item is in, we ask the item ...
        item: et.Element() <item>
        equip=False: set True if you want to set the equipped attribute of the item to 1.
        """

        container_id = int(item.get("inside","-1"))
        
        # of course only if it is currently packed ...
        if container_id >= 0:
            item_id = item.get("id")
            container = self.getItemById(str(container_id))
           
            # remove item from bag content by writing a new list of everything 
            # that is inside the container but the item we are packing out
            contents = container.get("content")
            content_ids = contents.split(" ")
            new_content = ""
            for entry in content_ids:
                if int(entry) != int(item_id):
                    new_content = new_content + " " + entry

            new_content = new_content.strip()           
            container.set("content",new_content)
           
            # set the item as unpacked (and equipped)
            item.set("inside","-1")
        if equip: item.set("equipped","1") 

        self.addEvent(item,op=msg.CHAR_ITEM_UNPACKED)
        self.addEvent(container,op=msg.CHAR_ITEM_UNPACKED_BAG)
    
    # this method returns the weight of an item and all subitems
    def getWeight(self,item):
        weight = 0
        if item is not None: 
            weight = int(item.get("weight","0")) * int(item.get("quantity","0"))
            content = item.get("content","")
            content_list = content.split()
            for item_id in content_list:
                sub_item = self.getItemById(str(item_id))
                if sub_item is not None:
                    # add the weight of this item
                    sub_quantity = int(sub_item.get("quantity","1"))
                    sub_weight = int(sub_item.get("weight","0")) * sub_quantity
                    weight = weight + sub_weight

                    # add potentials contents to the list ...
                    sub_content = sub_item.get("content","")
                    sub_content_list = sub_content.split()
                    for sub_id in sub_content_list: content_list.append(str(sub_id))

        return weight

    # retrieve one item from the inventory that is identical to the one we are checking
    def getIdenticalItem(self,item):
        """ get one item that is 'identical' to the one to check
        item: an et.Element() <item> that we want to find a match for
        returns: et.Element() <item> so similar to the input, that we can just stack them (or None)
        """
        identical_item = None
        item_name = item.get("name")
        item_options = item.findall("option")
        item_quality = item.get("quality")
        item_id = item.get("id","x")
        item_inside = item.get("inside","-1")
        
        # items with content can never be identical ..
        item_content = item.get("content","")
        # equipped items can't be identical 
        item_equipped = int(item.get("equipped","0"))

        if (item_content == "" and 
            item_equipped == 0):

            # okay let's look through the other items
            current_items = self.getItems(item_name)
            for current_item in current_items:
                # our premise ...
                identical = True

                # get the data for the first check ...
                cur_id = current_item.get("id")
                cur_equipped = current_item.get("equipped","0")
                cur_inside = current_item.get("inside","-1")
                cur_quality = current_item.get("quality")
                # compare quality and item location. 
                # make sure it is not actually the same item!!
                if (int(cur_quality) == int(item_quality) and 
                    int(cur_inside) == int(item_inside) and 
                    int(cur_equipped) != 1 and
                    (cur_id != item_id)):

                    # compare item options
                    cur_options = current_item.findall("option")
                
                    for cur_option in cur_options:
                        for item_option in item_options:
                            if ((item_option.get("name") == cur_option.get("name")) and
                            (item_option.get("value") != cur_option.get("value"))):
                                identical = False
                # nope they are different for sure (or literally the same)
                else: identical = False
            
                # this is probably another instance of this item ...
                if identical: 
                    # let's check the description
                    cur_description = current_item.find("description")
                    if cur_description is not None: cur_description = cur_description.text
                    new_description = item.find("description")
                    if new_description is not None: new_description = new_description.text
                    if cur_description is None: cur_description = " "
                    if new_description is None: new_description = " "
                    if cur_description != new_description: identical = False
                # yes we are sure they are identical
                if identical:
                    identical_item = current_item
                    break
            
        return identical_item
    
    # assign item to body
    def equipItem(self,item):
        item.set("equipped","1")
        self.addEvent(item,op=msg.CHAR_ITEM_EQUIP)

    # unassign item from body 
    def unequipItem(self,item):
        item.set("equipped","0")
        self.addEvent(item,op=msg.CHAR_ITEM_UNEQUIP)

    # this method reassigns item IDs
    def setItemIDs(self):
        items = self.getItems()
        id = 0
        for item in items:
            item.set("id",str(id))
            id = id + 1

    # retrieve the highest current id
    def getHighestItemID(self):
        items = self.getItems()
        id = 0
        for item in items:
            item_id = item.get("id")
            if item_id:
                item_id = int(item_id)
                if item_id > id: id = item_id
        return id

############Handling the characters funds
    
    # get a character account
    def getAccount(self,name = "0"):
        return self.xml_char.find(".//account[@name='"+name+"']")

    # get a character account
    def getAccounts(self):
        return self.xml_char.findall(".//account")
    
    # create an account
    def createAccount(self,name):
        """ create a new named account
        name: string - the name of the new account
        """
        account = self.xml_char.find(".//account[@name='"+name+"']")
        if account == None:
            account = et.Element("account",{"name",name})
            inventory = self.getInventory()
            inventory.append(account)

    # deleting an account
    def deleteAccount(self,name):
        """ this method removes the account of a character funds on that account will be transferred to '0'
        name: string - name of the account (the account '0' will not be deleted
        """
        # the main account can't be deleted!
        if name != "0":
            inventory = self.getInventory()
            account = inventory.find("account[@name='"+name+"']")
            if account != None:
                balance = self.getAccountBalance(name)
                self.updateAccount(-balance,name)
                self.updateAccount(balance)
                inventory.remove(account)
        
    def getAccountBalance(self,name = "0",type = float):
        account = self.xml_char.find(".//account[@name='"+name+"']")
        balance = account.get("balance")
        if type == float:
            balance = type(balance)
        if type == str:
            parts = balance.split(".")

        return balance

    def updateAccount(self,value,name = "0",reason=None):
        # update the account in the XML 
        account = self.xml_char.find(".//account[@name='"+name+"']")
        cur_balance = account.get("balance","0.0")
        new_balance = float(cur_balance) + float(value)
        account.set ("balance",str(new_balance))

        # retrieve the total balance variable
        total_balance = self.account_balance.get()
        total_balance = total_balance.replace(",",".")
        if not "." in total_balance: total_balance = 0.0
        total_balance = float(total_balance)
        total_balance = total_balance + float(value)

        total_balance = str(total_balance)
        total_balance = total_balance.replace(".",",")
        if "," in total_balance[-2:]: total_balance = total_balance + "0"
        self.account_balance.set(total_balance)

    # ########################Handling contact # #################################
    
    # create a new contact
    def newContact(self,name = ""):
        """ this method creates a new contact tag with a unique id and returns the id.
        name: string (optional) The name of the contact
        return: int - id of the contact (can than be used to load that contact for further editing)
        """
        id = self.getHighestContactId() + 1

        contact = et.Element("contact")
        contact.set("id",str(id))
        contact.set("name", str(name))

        contacts = self.xml_char.find("contacts")
        contacts.append(contact)

        return id

    # get a contact based on its id
    def getContactById(self,id):
        """ This method tries to retrieve a contact based on a given id.
        id: int (will be converted to string so it can be a string)
        return: et.Element() <contact>
        """
        id = str(id)
        contact = self.xml_char.find("./contacts/contact[@id='"+id+"']")
        return contact

    def removeContactById(self,id):
        contacts = self.xml_char.find("contacts")
        if contacts is not None:
            contact = contacts.find("contact[@id='"+id+"']")
            if contact is not None:
                contacts.remove(contact)

    def getContacts(self):
        """ this method will return all contacts
        return: [et.Element() <contact>, ...]
        """
        contacts = self.xml_char.findall("./contacts/contact")
        return contacts

    # find the highest current contact id
    def getHighestContactId(self):
        """ This method returns the highest contact id
        return: int (-1 if no contacts exist)
        """
        contacts = self.xml_char.findall("contacts/contact")
        highest_id = -1
        for contact in contacts:
            id = int(contact.get("id"))
            if id > highest_id: highest_id = id
        return highest_id


###########character image 
    

    # create or update reference to image
    def setImage(self,filename):
        image = self.xml_char.find("./basics/image")
        if image is not None:
            image.set("name",filename)
        else:
            basics = self.xml_char.find("./basics")
            image = et.SubElement(basics,"image",{"file":filename})

    
    # retrieve the image reference
    def getImage(self):
        return self.xml_char.find("./basics/image")

    # #
    def setImageSize(self,size,x,y,scale):
        image_tag = self.xml_char.find("./basics/image")
        size_tag = image_tag.find("size[@name='"+size+"']")
        if size_tag is None:
            et.SubElement(image_tag,"size",{"name":size,"x":str(x),"y":str(y),"scale":str(scale)})
        else:
            size_tag.set("x",str(x))
            size_tag.set("y",str(y))
            size_tag.set("scale",str(scale))

    def removeImage(self):
        basics_tag = self.xml_char.find("./basics")
        image_tag = basics_tag.find("image")
        basics_tag.remove(image_tag)


    # this adds a character modification event
    def addEvent(self,tag,mod=None,op=None):
        """ store a character modification inside the character xml

        tag (et.Element<any>) the character tag that is edited
        mod (string) - a modification information 
        op (string) - additional information on the transaction 

        """
        
        # create the event
        event = et.Element("event")
        date = datetime.now().strftime(msg.DATEFORMAT)
        event.set("date",date)
        event.set("element",tag.tag)

        if mod:
            event.set("mod",str(mod))
        if op:
            event.set("op",str(op))

        # add additional information based on the element
        # the transaction was performed on ... 
        if tag.tag == "attribute":
            name = tag.get("name")
            value = tag.get("value")
            event.set("name",name)
            event.set("value",value)
        elif tag.tag == "skill":
            id = tag.get("id")
            value = tag.get("value")
            event.set("id",id)
            if int(value) > 0: event.set("value",value)
        elif tag.tag == "trait":
            name = tag.get("name")
            xp = tag.get("xp")
            if op == msg.CHAR_TRAIT_REMOVED:
                xp = str(-int(xp))
            event.set("name",name)
            event.set("xp",xp)
        elif tag.tag == "data":
            name = tag.get("name")
            value = tag.get("value")
            event.set("name",name)
            event.set("value",value)
        elif tag.tag == "item":
            name = tag.get("name")
            id = tag.get("id")
            quantity = tag.get("quantity")
            event.set("name",name)
            event.set("id",id)
            event.set("quantity",quantity)
            event.set("hash", str(self.hashElement(tag)))


        # store the event
        events = self.xml_char.find("events")
        events.append(event)

        # generate and update the hash
        event_hash = self.hashElement(event)
        events_hash = int(events.get("hash","0"))
        events_hash += event_hash
        events.set("hash",str(events_hash))

    # generating an Element hash
    def hashElement(self,element):
        element_string = et.tostring(element)
        return hash(element_string)

    def getEvents(self):
        return self.xml_char.find("events")
    
            