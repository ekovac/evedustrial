import eve
from eve.general import skilltree
from eve.items import EveAssetList
from evecentral import MarketStats
a=eve.EveAccount('5215980','FB17D8197A1F408B9D0F1D41940337407E568909588C4008B81B23CBEE5F8E17')
a.refresh()
fox = a.characters[1]
fox.refresh()
assets = EveAssetList(fox)
assets.refresh()
#for i in assets.assets:
#    print i
ib = assets.get_item_bundle()
#print ib
#for i in fox.skills:
#    print i[0],i[2]
print ib.get_bundle_price()
