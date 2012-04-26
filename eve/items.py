from . import EVE_BASE_URL
from . xml import EveXml
from lxml import etree
from . db import game_db as db
EVE_ASSETLIST = EVE_BASE_URL + 'char/AssetList.xml.aspx'
from evecentral import MarketStats
class ItemDB(object):
    def __init__(self):
        self.items = dict()
    def get_item(self, id):
        if not self.items.has_key(id):
            self.items[id]=ItemType(db.get_item_row(id))
        return self.items[id]
item_db = ItemDB()
class ItemType(object):
    def __init__(self, row):
        self.id = row["typeID"]
        self.name = row["typeName"]
        self.desc = row["description"]
        self.volume = row["volume"]
        return
    def __str__(self):
        return self.name
class ItemBundle(object):
    def __init__(self, items={}):
        self.item_list = dict(items)
    def __mul__(self, other):
        pass
    def __add__(self, other):
        it = ItemBundle(self.item_list)

        if other.__class__ == ItemBundle:
            for ib_key in other.item_list:
                if not it.item_list.has_key(ib_key):
                    it.item_list[ib_key]=other.item_list[ib_key]
                else:
                    it.item_list[ib_key]+=other.item_list[ib_key]

        elif other.__class__ == EveAsset:
            if not it.item_list.has_key(other.item_type):
                it.item_list[other.item_type] = other.quantity
            else:
                it.item_list[other.item_type] += other.quantity

        elif other.__class__ == ItemType:
            if not it.item_list.has_key(other):
                it.item_list[other] = 1
            else:
                it.item_list[other] += 1
        else:
            raise TypeError

        return it
    def get_bundle_price(self, region=None):
        itemids = self.item_list.keys()
        itemids = map(lambda x: x.id, itemids)
        itemvalues = MarketStats.query(itemids, region)
        tot = 0
        tot = reduce(lambda a,b: a+b[1]*itemvalues[b[0].id].buystats['median'], self.item_list.items(), 0)
        return tot
    def __str__(self):
        lines = list()
        for key in self.item_list:
            lines.append("%d %s" % (self.item_list[key], key.name))
        return "\n".join(lines)
class EveAsset(object):
    def __init__(self, assetnode):
        xmlroot = assetnode
        self.item_type = item_db.get_item(int(xmlroot.attrib['typeID']))
        self.contents = list()
        try:
            self.quantity = int(xmlroot.attrib['quantity'])
        except KeyError:
            self.quantity = 1
        try:
            self.location = int(xmlroot.attrib['locationID'])
        except KeyError:
            self.location = None
        rowset = xmlroot.getchildren()
        if (len(rowset) > 0):
            rowset=rowset[0].getchildren()
            for child in rowset:
                child = EveAsset(child)
                self.contents.append(child)
        return
    def get_item_bundle(self):
        ib = ItemBundle()
        for i in self.contents:
            ib = ib + i
        ib = ib + self
        return ib
    def __str__(self):
        return "%dx %s" % (self.quantity, str(self.item_type) )
class EveAssetList(EveXml):
    def __init__(self, character):
        super(EveAssetList,self).__init__()
        self.url = EVE_ASSETLIST
        self.args = character.args
        self.character = character
        self.assets = list()
    def parse_xml(self):
        self.assets = list()
        super(EveAssetList,self).parse_xml()
        xmlroot = self.xmlroot.xpath("/eveapi/result/rowset[@name='assets']")[0]
        for assetrow in xmlroot:
            """ Only adds toplevel assets; need to walk down Asset tree otherwise. """
            a = EveAsset(assetrow)
            self.assets.append(a)
        return
    def get_item_bundle(self, locid=None):
        """ Get an itembundle that represents all assets within a certain location or the universe. """
        ib = ItemBundle()
        for asset in self.assets:
            ib = ib + asset.get_item_bundle()
        return ib
