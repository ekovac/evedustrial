from . xml import EveXml
from . xml import EveXmlException
from . import EVE_BASE_URL
EVE_SKILLTREE = EVE_BASE_URL + 'eve/SkillTree.xml.aspx'
EVE_REFTYPES = EVE_BASE_URL + 'eve/RefTypes.xml'
#print EVE_SKILLTREE
class EveSkill:
    def __init__(self, xmlnode):
         self.parse_xml(xmlnode)
    def parse_xml(self, xmlnode):
        self.requiredskills = list()
        try:
            self.primaryattrib = xmlnode.xpath("requiredAttributes/primaryAttribute")[0].text
            self.secondaryattrib = xmlnode.xpath("requiredAttributes/secondaryAttribute")[0].text
        except:
            self.primaryattrib = None
            self.secondaryattrib = None
        self.name = xmlnode.attrib['typeName']
        self.id = int(xmlnode.attrib['typeID'])
        self.description = xmlnode.xpath("description")[0].text
        self.multiplier = xmlnode.xpath("rank")[0].text
        for skillreq in xmlnode.xpath("rowset[@name='requiredSkills']/row"):
            self.requiredskills.append( (int(skillreq.attrib['typeID']), int(skillreq.attrib['skillLevel'])) )
    def __str__(self):
        return self.name 
class EveSkillGroup:
    def __init__(self, xmlnode):
        self.skills = dict()
        self.parse_xml(xmlnode)
    def parse_xml(self, xmlnode):
        self.name = xmlnode.attrib['groupName']
        self.id = int(xmlnode.attrib['groupID'])
        skills = xmlnode.xpath("rowset[@name='skills']/row")
        for skill in skills:
            skill = EveSkill(skill)
            id = skill.id
            self.skills[id] = skill
class EveSkillTree(EveXml):
    def __init__(self):
        super(EveSkillTree,self).__init__()
        self.args = dict()
        self.skillgroups = list()
        self.skills = dict()
        self.url = EVE_SKILLTREE
    def parse_xml(self):
        super(EveSkillTree,self).parse_xml()
        xmlroot = self.xmlroot
        xmlroot = xmlroot.xpath("/eveapi/result")[0]
        self.skillgroups = list()
        self.skills = dict()
        for group in xmlroot.xpath("rowset[@name='skillGroups']/row"):
            group = EveSkillGroup(group)
            self.skillgroups.append(group)
            for id,skill in group.skills.items():
                self.skills[id] = skill
skilltree = EveSkillTree()
skilltree.refresh()
