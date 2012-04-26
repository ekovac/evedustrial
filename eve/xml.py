from xdg import BaseDirectory
import time
import os
import urllib
from urllib2 import urlopen
from lxml import etree

EVECACHEPATH=os.path.join(BaseDirectory.xdg_cache_home, "evedustrial")
class EveXmlException(Exception):
    def __init__(self, trouble_element):
        self.element = trouble_element

class EveXml(object):
    """ 
    This class is responsible for handling the generic elements which 
    exist in all Eve API objects, such as timestamp, caching style, 
    and other metadata.
    """

    def __init__(self):
        self.fetchedtime = None
        self.cacheduntil = None
        self.api_version = None
        self.xml = None
        self.is_shortcache = False
        self.label = type(self).__name__
    
    def cached_name(self):
        name = os.path.join(EVECACHEPATH, self.label + "_" + 
            "_".join(self.args.values())+ ".xml")
        return name

    def refresh(self, force=False):
        self.update_xml(force)
        self.parse_xml()

    def update_xml(self, force=False):
        fname = self.cached_name()
        if force and self.is_short_cache:
            # Forcing an update on short_cache stuff 
            # won't help us. 
            return
        if (os.path.exists(fname) and not force):
            f = open(fname, 'r')
            self.xml = f.read()
            f.close()
            self.parse_xml()
        if (self.cacheduntil < time.gmtime()) or force:
            url_args = urllib.urlencode(self.args)
            self.xml = urlopen(self.url, url_args).read()
            if not os.path.exists(EVECACHEPATH):
                os.makedirs(EVECACHEPATH)
            f = open(fname, 'w')
            f.write(self.xml)

    def parse_xml(self):
        if not self.xml:
            self.update_xml()
        self.xmlroot = etree.fromstring(self.xml)
        xmlroot = self.xmlroot
        eveapi = xmlroot.xpath("/eveapi")
        self.api_version = float(eveapi[0].attrib["version"])

        fetchedtime = xmlroot.xpath("/eveapi/currentTime")
        fetchedtime = fetchedtime[0].text
        fetchedtime = time.strptime(fetchedtime, "%Y-%m-%d %H:%M:%S")
        self.fetchedtime = fetchedtime

        cacheduntil = xmlroot.xpath("/eveapi/cachedUntil")
        cacheduntil = cacheduntil[0].text
        cacheduntil = time.strptime(cacheduntil, "%Y-%m-%d %H:%M:%S")
        self.cacheduntil = cacheduntil
 
        return
