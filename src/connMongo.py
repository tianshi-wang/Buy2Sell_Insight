import pymongo
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from pymongo import MongoClient

def conn(pwInv, pwDomain):
    category_client = MongoClient('mongodb://%s@ds054069-a1.zwn31.fleet.mlab.com:54062/covetly-domain-inventory-main?ssl=true' %(pwInv))
    domain_client=MongoClient('mongodb://%s@ds034887-a1.zwn31.fleet.mlab.com:34882/covetly-domain?ssl=true' %(pwDomain))

    domainDB=domain_client['covetly-domain']
    #print(domainDB.list_collection_names())
    # #Show all the collections (tables in SQL) on Domain server
    #['collectionitems', 'featuredassets', 'featureditems', 'objectlabs-system', 'objectlabs-system.admin.collections',
    # 'wantlistitems', 'livebids', 'sellers', 'buybids', 'storeadminusers', 'orders', 'inventoryitems', 'users']

    categoryDB=category_client['covetly-domain-inventory-main']
    #print(categoryDB.list_collection_names())
    # #All the collections on Category server
    #['modules', 'moduleitems', 'objectlabs-system.admin.collections', 'system.indexes', 'objectlabs-system', 'modulecategories']
    return categoryDB, domainDB



# Example: plot data
# from ggplot import *
#
# p = ggplot(aes(x='Amount'), data=domainDF)
# p + geom_histogram(binwidth=20)
# p + geom_density()





