import os
from xdg import BaseDirectory
import sqlite3 as sqlite
EVE_CENTRAL_BASE_URI="http://api.eve-central.com/api/"
EVE_CENTRAL_CACHE_PATH=os.path.join(BaseDirectory.xdg_cache_home, "evecentral")
from marketstat import *
#from quicklook import *
