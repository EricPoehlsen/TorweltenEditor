# coding=utf-8

import os
import xml.etree.ElementTree as et
import tkinter as tk

class SkillTree():
    def __init__(self):
        # this is the xml interpretation of the character
        self.xml_skills = None
        self.loadTree()

    
    def loadTree(self,filename = None):
        self.xml_skills = et.parse('data/skills.xml')

    def groups():
        result = []
        groups = self.xml_skills.findall(".//skillgroup")
        for group in groups:
            name = group.get("name")
            type = group.get("type")
            minid = group.get("minid")
            maxid = group.get("maxid")
            result.append((name,type,minid,maxid))
        return result

    # get skills from minimum specialization, maximum specialization
    def list(self,minspec = 1,maxspec = 3):

        result = []

        skills = self.xml_skills.findall(".//skill")
        for skill in skills:
            name = skill.get("name")
            spec = int(skill.get("spec"))
            id = int(skill.get("id"))
            
            if ((minspec <= spec) and (spec <= maxspec)):
                result.append((name,spec,id))
                
        return result

    def getSkill(self,name):
        skill = self.xml_skills.find(".//skill[@name='"+name+"']") 
        return skill

    # this creates a new skill and stores it in the skill
    def newSkill(self,name,origin):
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
            min_id = int(group.get("minid","0"))
            max_id = int(group.get("maxid","0"))
            if min_id <= origin_id <= max_id:
                relevant_group = group
                break

        cur_skills = relevant_group.findall("skill[@parent='"+str(parent)+"']")
        new_num = len(cur_skills) + 1
        if spec == 2: 
            id = parent + (new_num * 100)
        if spec == 3:
            id = parent + new_num

            
            skill = et.Element("skill",{"name":str(name),
                                        "id":str(id),
                                        "parent":str(parent),
                                        "spec":str(spec),
                                        "type":origin_type})
            relevant_group.append(skill)
            self.sortSkills(relevant_group)

        with open("data/skills.xml", mode = "wb") as file:
            self.xml_skills.write(file,encoding = "utf-8", xml_declaration=True)
        

    # returns a single skill element by Id
    def getSkillById(self, id):
        id = str(id)
        xml_skill = self.xml_char.find(".//skill[@name='"+str(id)+"']")
        return xml_skill

    def sortSkills(self,group):
        skill_list = []
        for skill in group:
            key = skill.get("id")
            skill_list.append((key,skill))
        skill_list.sort()
        # overwriting the skills ... 
        group[:] = [new_skill[-1] for new_skill in skill_list]


    # Writing parents based on the ID of a skill. 
    def repairParents(self):
        skills = self.xml_skills.findall(".//skill")
        for skill in skills:
            id = skill.get("id")
            spec = skill.get("spec")
            if (spec == "1"):
                parent = "0"
                skill.set("parent", parent)

            if (spec == "2"):
                parent = id[:2] + "0000"
                skill.set("parent", parent)

            if (spec == "3"):
                parent = id[:4] + "00"
                skill.set("parent", parent)

        with open("data/skill.xml", mode = "wb") as file:
           self.xml_skills.write(file,encoding = "utf-8", xml_declaration=True)
           file.close()
