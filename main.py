import eve
from eve.general import skilltree
from eve.items import EveAssetList
from evecentral import MarketStats
a=eve.EveAccount('999889', 'jTZlVa8KilYrOFkTalaD738e10En3ZlSO6w6p83gsM0cnoPdHRfvvwTbsSOXIaXR')
a.refresh()
print a
fox = a.characters[1]
fox.refresh()
assets = EveAssetList(fox)
assets.refresh()
ib = assets.get_item_bundle()
print ib
#print ib
#for i in fox.skills:
#    print i[0],i[2]
print ib.get_bundle_price()
