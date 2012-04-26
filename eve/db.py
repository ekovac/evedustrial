from . xml import EVECACHEPATH
import time
import os
import urllib
import sqlite3 as sqlite
from urllib2 import urlopen

class EveDb(object):
    """
    This class is responsible for loading up an instance of the eve static
    dump information. Without this, most functionality of this library will
    not work. """
    def __init__(self):
        self.db = sqlite.connect(EVECACHEPATH+"/eve.db")
        self.db.row_factory = sqlite.Row
        if not self.db:
            print "Failed to init database; all calls to EveDb will fail."
    def get_item_row(self, id):
        c=self.db.cursor()
        c.execute("select typeID,typeName,description,volume from invTypes where typeID == %d" % id)
        itemrow = c.fetchone()
        return itemrow
    def get_location_row(self, id):
        return
    def get_location_by_string(self, id):
        return
    def get_item_by_string(self, txt):
        c=self.db.cursor()
        c.execute("select typeID,typeName,description,volume from invTypes where typeName GLOB '%s'" % txt)
game_db=EveDb()
