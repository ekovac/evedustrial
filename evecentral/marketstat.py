import sqlite3 as sqlite
from lxml import etree
from urllib2 import urlopen
from urllib import urlencode
from . import EVE_CENTRAL_BASE_URI, EVE_CENTRAL_CACHE_PATH
import time
IS_OLD=24

def dict_from_list(keyfunc, l):
    """ Generate a dictionary from a list where the keys for each element are generated based off of keyfunc. """
    result = dict()
    for item in l:
        result[keyfunc(item)] = item
    return result
def dict_merge(a,b):
    c = dict()
    for k in a:
        c[k] = a[k]
    for k in b:
        c[k] = b[k]
    return c
class MarketStatEntry(object):
    def __init__(self, template, region=None):
        self.typeid = None
        self.region = None
        self.buystats = dict()
        self.sellstats = dict()
        self.fetched = None
        if type(template) == type(etree.Element("xml")):
            self.init_from_xml(template, region)
        else:
            try:
                self.init_from_row(template)
            except:
                raise TypeError
    def init_from_row(self, row):
        self.fetched = row['fetched']
        self.typeid = row['typeid']
        self.region = row['region']
        self.buystats = {'volume':row['buyvol'], 'mean':row['buyavg'], 'median':row['buymed'], 'maximum':row['buymax'], 'minimum':row['buymin'], 'stddev':row['buydev']}
        self.sellstats = {'volume':row['sellvol'], 'mean':row['sellavg'], 'median':row['sellmed'], 'maximum':row['sellmax'], 'minimum':row['sellmin'], 'stddev':row['selldev']}

    def init_from_xml(self, xmlnode, region=None):
        self.fetched = time.time() # XML is always fetched at the latest moment
        self.typeid = int(xmlnode.get('id'))
        get_buy = lambda attr: float(xmlnode.xpath("buy/"+attr)[0].text)
        self.buystats['volume'] = get_buy('volume')
        self.buystats['mean'] = get_buy('avg')
        self.buystats['maximum'] = get_buy('max')
        self.buystats['minimum'] = get_buy('min')
        self.buystats['stddev'] = get_buy('stddev')
        self.buystats['median'] = get_buy('median')
        get_sell = lambda attr: float(xmlnode.xpath("sell/"+attr)[0].text)
        self.sellstats['volume'] = get_sell('volume')
        self.sellstats['mean'] = get_sell('avg')
        self.sellstats['maximum'] = get_sell('max')
        self.sellstats['minimum'] = get_sell('min')
        self.sellstats['stddev'] = get_sell('stddev')
        self.sellstats['median'] = get_sell('median')
        if region:
            self.region = region
        else:
            self.region = -1
    def __str__(self):
        return ""
class MarketStatApi(object):
    def __init__(self):
        self.init_cachedb()
    def init_cachedb(self):
        self.cachedb = sqlite.connect(EVE_CENTRAL_CACHE_PATH+"/marketstat.db")
        self.cachedb.row_factory = sqlite.Row
        c=self.cachedb.cursor()
        c.execute("""create table if not exists marketstat(typeid,region,buyvol,buyavg,buymed,buymax,buymin,buydev,sellvol,sellavg,sellmed,sellmax,sellmin,selldev,fetched)""")
    def update_cache(self, market_elements):
        c = self.cachedb.cursor()
        for e in market_elements.values():
            etup = (e.typeid, e.region, e.buystats['volume'], e.buystats['mean'], e.buystats['median'], e.buystats['maximum'], e.buystats['minimum'], e.buystats['stddev'], 
                    e.sellstats['volume'], e.sellstats['mean'], e.sellstats['median'], e.sellstats['maximum'], e.sellstats['minimum'], e.sellstats['stddev'], e.fetched)
            c.execute("insert into marketstat values %s" % (etup,))
        self.cachedb.commit()
        return
    def query_cache(self, typeids, region=None):
        c = self.cachedb.cursor()
        # Godawful hack to work around fact that (1,) isn't liked much by SQL
        # This results in (-1,1) being the shortest possible tuple sent, eliminating this risk.
        if (len(typeids) < 2):
            typeids = (-1,) + tuple(typeids)
        oldthresh = time.time() - IS_OLD*60*60
        c.execute("delete from marketstat where fetched < ?", (oldthresh,)) # Clear out stale entries.
        if not region:
            print typeids
            c.execute("select * from marketstat where typeid in (" + 
                ",".join(("?",)*len(typeids)) + ")", tuple(typeids))
        else:
            c.execute("select * from marketstat where typeid in %s and region=%d" % (str(tuple(typeids)),region))
        a = c.fetchall()
        return dict_from_list(lambda i: i.typeid, map(lambda r: MarketStatEntry(r), a))
    def query_xml(self, typeids, region=None):
        # Create a list of tuples of the form ("typeid",typeid)
        typeidmap = map(lambda i: ("typeid", i), typeids)
        if region:
            regionmap = [("regionlimit", i),]
        else:
            regionmap = []
        args = typeidmap + regionmap
        args = urlencode(args)

        xmlresult = urlopen(EVE_CENTRAL_BASE_URI+"marketstat", args).read()
        xmlroot = etree.fromstring(xmlresult)

        xmlroot = xmlroot.xpath("/evec_api/marketstat")[0]
        return dict_from_list(lambda i: i.typeid, map(lambda x: MarketStatEntry(x, region), xmlroot.getchildren()))
    def query(self, typeids, region=None):
        requests=set(typeids)
        cache_results = self.query_cache(requests, region)
        cache_hits=set(cache_results.keys())
        cache_misses=requests-cache_hits
        print "Cache hits: %d\nCache Misses: %d" % (len(cache_hits), len(cache_misses))
        xml_results = dict()
        while cache_misses:
            newset = set()
            while len(newset) < 100 and cache_misses:
                newset.add(cache_misses.pop())
            xml_results = dict_merge(xml_results, self.query_xml(newset, region))
        self.update_cache(xml_results)
        return dict_merge(xml_results, cache_results)
MarketStats = MarketStatApi()
