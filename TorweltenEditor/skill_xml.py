import xml.etree.ElementTree as et


class SkillTree(object):
    def __init__(self, settings):
        # this is the xml interpretation of the Skills
        self.xml_skills = None
        self.settings = settings
        self.buildTree()

    def loadTree(self, filename=None):
        tree = None
        try:
            tree = et.parse(filename)
            root = tree.getroot()
            if root.tag == "expansion":
                skills = root.find("skills")
                if skills is not None:
                    tree = et.ElementTree(skills)
                else:
                    tree = None
        except (FileNotFoundError, et.ParseError) as e:
            print("Error load skill tree", filename, str(e))
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

    def buildTree(self):
        """ build the skill tree """

        self.xml_skills = self.loadTree("data/skills_de.xml")
        active_expansions = self.settings.getExpansions()
        for expansion in active_expansions:
            self.addToTree("expansion/"+expansion)

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
            parent = int(skill.get("parent"))
            if minspec <= spec <= maxspec:
                result.append((name, spec, id, parent))
        return result

    def getSkill(self, name):
        """ Retrieve a skill by name """

        skill = self.xml_skills.find(".//skill[@name='"+name+"']") 
        return skill

    def getSkillById(self, id):
        """ Retrieve a skill by id"""

        id = str(id)
        xml_skill = self.xml_skills.find(".//skill[@id='"+str(id)+"']")
        return xml_skill

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

    def newSkill(self, name, origin):
        """ Create a new skill and store it within the local skill expansion."""

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
        self.addToLocalSkills(skill)

    def addToLocalSkills(self, skill):
        """ Adds the given skill to the local skills expansion 
        
        Note:
            A new local skills expansion will be created if it does not exist.
            The local skills expansion will be activated! 
        
        """

        filename = "expansion/local_skills.xml"
        local = None
        with open(filename, mode="rb") as file:
            local = et.parse(filename)
        if local is not None:
            root = local.getroot()
            skills = root.find(".//skills")
            skills.append(skill)
        else:
            root = et.Element("expansion", {"name": "local"})
            et.SubElement(root, "meta", {"lang": "*"})
            skills = et.SubElement(root, "skills")
            skills.append(skill)
            local = et.ElementTree(root)

        with open(filename, 'wb') as file:
            local.write(file, encoding="utf-8", xml_declaration=True)
            self.settings.updateExpansions(filename.split("/")[1], include=True)
            self.settings.save()

    @staticmethod
    def sortSkills(group):
        """ sorting a group of skills in place """

        skill_list = []
        for skill in group:
            id = skill.get("id")
            name = skill.get("name")
            skill_list.append((id, name, skill))
        skill_list.sort()
        # overwriting the skills ...
        group[:] = [new_skill[-1] for new_skill in skill_list]

    def repairParents(self, filename):
        """ rewrites the parents of the skills based on their id
        
        Warning: 
            This is a utility method which pretty agressivly rewrites parents
            of skills and outputs the result to the specified file. 
        """

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

        with open(filename, mode="wb") as file:
            self.xml_skills.write(file, encoding="utf-8", xml_declaration=True)
