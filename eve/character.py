from . import EVE_BASE_URL
from . xml import EveXml
from . general import skilltree
import urllib
from urllib2 import urlopen
import lxml
EVE_ACCOUNT = EVE_BASE_URL + 'account/Characters.xml.aspx'
EVE_CHARSHEET = EVE_BASE_URL + 'char/CharacterSheet.xml.aspx'
EVE_INDUSTRY = EVE_BASE_URL + 'char/IndustryJobs.xml.aspx'
EVE_ORDERS = EVE_BASE_URL + 'char/MarketOrders.xml.aspx'
class EveAccount(EveXml):
    """ Contains character list; creates the EveCharacters, but does not refresh() them. """
    def __init__(self, key_id, vcode):
        super(EveAccount,self).__init__()
        self.key_id = key_id
        self.vcode = vcode
        self.characters = list()
        self.url = EVE_ACCOUNT
        self.args = {'keyID':self.key_id,'vCode':self.vcode}
    def parse_xml(self):
        super(EveAccount,self).parse_xml()
        xmlroot = self.xmlroot
        rows = xmlroot.xpath("/eveapi/result/rowset[@name=\"characters\"]/row")
        self.characters = list()
        for charentry in rows:
            charid = charentry.attrib['characterID']
            charname = charentry.attrib['name']
            corpname = charentry.attrib['corporationName']
            newchar = EveCharacter(self, charid, charname, corpname)
            self.characters.append(newchar)
    def __str__(self):
        result = "KeyID %s\n" % self.key_id
        result += "\n".join(map(str, self.characters))
        return result

class EveCharacter(EveXml):
    """ 
    Contains character sheet information, excluding assets and industry info; 
    those can be acquired from properties of this. 
    """
    def __init__(self, account, charid, name=None, corpname=None):
        super(EveCharacter,self).__init__()
        self.name = name
        self.corpname = corpname
        self.account = account
        self.charid = charid
        self.url = EVE_CHARSHEET
        self.args = {'characterID':charid}
        self.args.update(self.account.args)
    def parse_xml(self):
        super(EveCharacter,self).parse_xml()
        xmlroot = self.xmlroot
        xmlroot = xmlroot.xpath("/eveapi/result")[0]
        # Fluff
        getmacro = lambda x: xmlroot.xpath(x)[0].text
        self.name = getmacro("name")
        self.race = getmacro("race")
        self.bloodline = getmacro("bloodLine")
        self.gender = getmacro("gender")
        self.corpname = getmacro("corporationName")
        self.corpid = getmacro("corporationID")
        self.clonetype = getmacro("cloneName")
        self.cloneSP = int(getmacro("cloneSkillPoints"))
        self.iskbalance = float(getmacro("balance"))
        # Attributes
        getmacro = lambda x: xmlroot.xpath("/attributes/"+x)
        self.intelligence = getmacro("intelligence")
        self.memory = getmacro("memory")
        self.charisma = getmacro("charisma")
        self.perception = getmacro("perception")
        self.willpower = getmacro("willpower")
        # Skills
        self.skills = list()
        for x in xmlroot.xpath("/eveapi/result/rowset[@name='skills']")[0]:
            skillid = int(x.attrib['typeID'])
            skillpoints = int(x.attrib['skillpoints'])
            level = int(x.attrib['level'])
            self.skills.append( (skilltree.skills[skillid], skillpoints, level) )
        self.certs = list()
        for x in xmlroot.xpath("/eveapi/result/rowset[@name='certificates']")[0]:
            certid = int(x.attrib['certificateID'])
            self.certs.append(certid)
        return
    def __str__(self):
        return "%s of %s" % (self.name, self.corpname)
