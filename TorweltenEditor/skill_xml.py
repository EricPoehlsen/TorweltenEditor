import os
import xml.etree.ElementTree as et
import tkinter as tk


class SkillTree(object):
    def __init__(self):
        # this is the xml interpretation of the character
        self.xml_skills = self.loadTree()
        self.addToTree("data/own_skills.xml")
        self.addToTree("data/the_linguist.xml")

    def loadTree(self, filename='data/skills.xml'):
        tree = None
        try:
            tree = et.parse(filename)
        except FileNotFoundError:
            pass
        return tree

    def addToTree(self, filename=None):
        """ Adding another set of skills to the skill tree

        Args:
            filename (str): the file to parse
        """

        if filename is None:
            filename = "data/demo_skills.xml"

        local_tree = self.loadTree(filename)

        skills = local_tree.findall(".//skill")
        groups = self.xml_skills.findall("skillgroup")
        for skill in skills:
            name = skill.get("name")
            existing_skill = self.getSkill(name)
            if existing_skill is None:
                id = int(skill.get("id", "0"))
                relevant_group = None

                for group in groups:
                    min_id = int(group.get("minid", "0"))
                    max_id = int(group.get("maxid", "0"))
                    if min_id <= id <= max_id:
                        relevant_group = group
                        break
                relevant_group.append(skill)
                self.sortSkills(relevant_group)

    def getList(self, minspec=1, maxspec=3):
        """ Get a list of skills

        Args:
            minspec (int): minimum specialization level
            maxspec (int): maximum specialization level

        Returns:
            [(name(str), spec(str), id(str)),...]
        """

        result = []
        skills = self.xml_skills.findall(".//skill")
        for skill in skills:
            name = skill.get("name")
            spec = int(skill.get("spec"))
            id = int(skill.get("id"))
            if minspec <= spec <= maxspec:
                result.append((name, spec, id))
        return result

    def getSkill(self, name):
        skill = self.xml_skills.find(".//skill[@name='"+name+"']") 
        return skill

    def getChildren(self, id):
        """ Gets the children or siblings of a skill:

        Args:
            id (int) - skill id
        """

        id = str(id)
        base = self.xml_skills.find(".//skill[@id='"+id+"']")
        search_id = -1
        if base is not None:
            spec = int(base.get("spec"))

            if spec < 3:
                search_id = base.get("id")
            else:
                search_id = base.get("parent")

        skills = self.xml_skills.findall(".//skill[@parent='"+search_id+"']")
        return skills

    # this creates a new skill and stores it in the skill
    def newSkill(self, name, origin):
        origin = self.getSkill(origin)

        origin_spec = int(origin.get("spec"))
        origin_id = int(origin.get("id"))
        origin_type = origin.get("type")
        if origin_spec == 3:
            parent = int(origin.get("parent"))
            spec = origin_spec
        else:
            parent = origin_id
            spec = origin_spec + 1

        relevant_group = None
        groups = self.xml_skills.findall("skillgroup")
        for group in groups: 
            min_id = int(group.get("minid", "0"))
            max_id = int(group.get("maxid", "0"))
            if min_id <= origin_id <= max_id:
                relevant_group = group
                break

        cur_skills = relevant_group.findall("skill[@parent='"+str(parent)+"']")
        new_num = len(cur_skills) + 1
        if spec == 2: 
            id = parent + (new_num * 100)
        if spec == 3:
            id = parent + new_num

        skill = et.Element(
            "skill",
            {"name": str(name),
             "id": str(id),
             "parent": str(parent),
             "spec": str(spec),
             "type": origin_type
            }
        )
        relevant_group.append(skill)
        self.sortSkills(relevant_group)
        self.updateLocalSkills(skill)

    def updateLocalSkills(self,skill):
        filename = "data/own_skills.xml"
        local = self.loadTree(filename)
        if local is not None:
            root = local.getroot()
            root.append(skill)
        else:
            root = et.Element("skills")
            root.append(skill)
            local = et.ElementTree(root)
        with open(filename, mode="wb") as file:
            local.write(file, encoding="utf-8", xml_declaration=True)

    # returns a single skill element by Id
    def getSkillById(self, id):
        id = str(id)
        xml_skill = self.xml_skills.find(".//skill[@id='"+str(id)+"']")
        return xml_skill

    def sortSkills(self, group):
        skill_list = []
        for skill in group:
            id = skill.get("id")
            name = skill.get("name")
            skill_list.append((id,name, skill))
        skill_list.sort()
        # overwriting the skills ...
        group[:] = [new_skill[-1] for new_skill in skill_list]

    # Writing parents based on the ID of a skill. 
    def repairParents(self):
        skills = self.xml_skills.findall(".//skill")
        for skill in skills:
            id = skill.get("id")
            spec = skill.get("spec")
            if spec == "1":
                parent = "0"
                skill.set("parent", parent)
            if spec == "2":
                parent = id[:2] + "0000"
                skill.set("parent", parent)
            if spec == "3":
                parent = id[:4] + "00"
                skill.set("parent", parent)

        with open("data/skill.xml", mode="wb") as file:
            self.xml_skills.write(file, encoding="utf-8", xml_declaration=True)
