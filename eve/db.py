from . xml import EVECACHEPATH
import time
from os import path
import urllib
import MySQLdb as mysql
from urllib2 import urlopen
class EveDb(object):
    """
    This class is responsible for loading up an instance of the eve static
    dump information. Without this, most functionality of this library will
    not work. """
    def __init__(self, database, user, passwd, host="localhost"):
        self.db = mysql.connect(host=host, user=user, passwd=passwd, db=database)
        
    def get_item_row(self, id):
        cur=self.db.cursor()
        cols = ("typeID", "typeName", "description", "volume")
        cur.execute("select "+ ",".join(cols) + " from invTypes where typeID = %s", (id,))
        row = cur.fetchone()
        row = dict(zip(cols, row))
        print row
        return row
    def get_location_row(self, id):
        return
    def get_location_by_string(self, id):
        return
    def get_item_by_string(self, txt):
        c = self.db.cursor()
        c.execute("select typeName from invTypes where typeName GLOB '%s'", (txt,))
        row = c.fetchone()
        return row["typeName"]
game_db=EveDb("eve", "eve", "eve")

