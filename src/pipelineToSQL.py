import connMongo
import pymongo
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import datetime as dt
import sys

def createDB():
    # Define a database name (we're using a dataset on births, so we'll call it birth_db)
    # Set your postgres username
    dbname = 'insightProj'
    username = 'Vera'  # change this to your username
    engine = create_engine('postgres://%s@localhost/%s' % (username, dbname))
    print(engine.url)
    if not database_exists(engine.url):
        create_database(engine.url)
    print(database_exists(engine.url))
    return engine

def encodeDate(df,created_date):
    df['month'] = df[created_date].apply(lambda x: '{:02.0f}'.format((x.year-2017)*12+x.month)+'-') #"added month index 2017-01 as 1"
    df = df.drop(['created_date', 'month'], axis=1)
    return df

def downloadOrder(domainDB,engine):
    db = domainDB.orders
    df = pd.DataFrame(columns=['order_id','userId', 'created_date','Amount','item_id', 'seller_id'])
    for doc in db.find({}, { \
            "_id":"$_id", \
            "UserId":"$UserId",\
            "CreatedDate": "$CreatedDate", \
            "Items.Amount": "$Items.Amount", \
            "Items.ItemId":"$Items.ItemId",\
            "Items.SellerId": "$Items.SellerId"\
            }).sort('_id', -1):
        newRowDF = pd.DataFrame([[\
            doc['_id'], doc['UserId'], doc['CreatedDate'], doc['Items'][0]['Amount'],doc['Items'][0]['ItemId'],doc['Items'][0]['SellerId']  \
            ]], columns=['order_id','userId', 'created_date','Amount','item_id', 'seller_id'])
        df = df.append(newRowDF, ignore_index=True)
    df.to_sql('orders', engine, if_exists='replace')
    return df


def downloadCollections(domainDB,engine):
    db = domainDB.collectionitems
    df_collections = pd.DataFrame(columns=[\
        'created_date','userId','itemId', 'itemName','module',"tags"])
    idx=0
    for doc in db.find({}, { \
        "CreatedDate": "$CreatedDate",
        "UserId": "UserId",
        "ItemId": "$ItemId",
        "Item.Name": "$Item.Name",
        "Item.SeoFriendlyModuleName": "$Item.SeoFriendlyModuleName",
        "Item.Tags": "$Item.Tags"
            }).sort([('_id',pymongo.DESCENDING)]):
        idx+=1
        try:
            newRowDF = pd.DataFrame([[ \
                doc['CreatedDate'], doc['UserId'],doc['ItemId'],doc['Item']['Name'], doc['Item']['SeoFriendlyModuleName'], \
                doc['Item']['Tags'] \
                ]], columns=['created_date','userId','itemId', 'itemName','module',"tags"]\
                )
            df_collections = df_collections.append(newRowDF, ignore_index=True)
            if idx%10000==0:
                print(str(idx))
                df_collections.to_sql('collections', engine, if_exists='append')
                df_collections = pd.DataFrame(columns=[ \
                     'created_date', 'userId', 'itemId', 'itemName', 'module', "tags"])
        except:
            print("Loading data error at line"+str(idx))
    df_collections.to_sql('collections', engine, if_exists='append')


def downloadWishList(domainDB,engine):
    db = domainDB.wantlistitems
    columnName=['created_date','userId','itemId','category']
    df_wishlist = pd.DataFrame(columns=columnName)
    idx=0
    for doc in db.find({}, { \
        "CreatedDate": "$CreatedDate",
        "UserId": "UserId",
        "Item._id": "$Item._id",
        "Item.CategoryName": "$Item.CategoryName",
            }):
        idx+=1
        try:
            newRowDF = pd.DataFrame([[ \
                doc['CreatedDate'], doc['UserId'],doc['Item']['_id'], doc['Item']['CategoryName'], \
                ]], columns=columnName\
                )
            df_wishlist = df_wishlist.append(newRowDF, ignore_index=True)
            if idx%10000==0:
                print(str(idx))
                df_wishlist.to_sql('wishlist', engine, if_exists='append')
                df_wishlist = pd.DataFrame(columns=columnName)
        except:
            print("Loading data error at line"+str(idx))
    df_wishlist.to_sql('wishlist', engine, if_exists='append')


def downloadItems(categoryDB,engine):
    db = categoryDB.moduleitems
    df = pd.DataFrame(columns=['itemId','name', 'ModuleName', 'CategoryName'])
    idx=0
    for doc in db.find({}, { \
        "_id": "$_id",
        "Name": "$Name",
        "SeoFriendlyModuleName": "$SeoFriendlyModuleName",
        "SeoFriendlyCategoryName": "$SeoFriendlyCategoryName"
            }).sort([('_id',pymongo.DESCENDING)]):
        idx+=1
        if idx%1000==0:
            print(idx)
        try:
            newRowDF = pd.DataFrame([[ \
                doc['_id'],doc['Name'],doc['SeoFriendlyModuleName'], doc['SeoFriendlyCategoryName']\
                ]], columns=['itemId','name', 'ModuleName', 'CategoryName']\
                )
            df = df.append(newRowDF, ignore_index=True)
        except:
            print("Loading data error at line"+str(idx))
    df.to_sql('items', engine, if_exists='replace')


def downloadUsers(domainDB,engine):
    """
    Write active (last login < 6 month and email is not Null) user list to user table
    :return: id, email, acount created month, last login month
    """
    db = domainDB.users
    df = pd.DataFrame(columns=[ \
        'userId', 'email', 'CreatedDate', 'LastLoginDate'])
    idx=0
    for doc in db.find({}, { \
        "_id": "$_id",
        "Profile.Email": "$Profile.Email",
        "CreatedDate": "$CreatedDate",
        "FirebaseProfile.LastLoginDate":"$FirebaseProfile.LastLoginDate"
            }):
        idx+=1
        if idx%1000==0:
            print(idx)
        try:
            newRowDF = pd.DataFrame([[ \
                doc['_id'],doc['Profile']['Email'],doc['CreatedDate'], doc['FirebaseProfile']['LastLoginDate'] \
                ]], columns=['userId','email', 'CreatedDate','LastLoginDate']\
                )
            df = df.append(newRowDF, ignore_index=True)
        except:
            print("Loading data error at line"+str(idx))
    df['month'] = df['CreatedDate'].apply(lambda x: (x.year - 2017) * 12 + x.month)  # "added month index 2017-01 as 1"
    df['lastLoginMonth'] = df['LastLoginDate'].apply(lambda x: (x.year - 2017) * 12 + x.month)
    df = df.drop(['CreatedDate','LastLoginDate'], axis=1)
    currentMonth = (dt.datetime.today().year-2017) * 12+dt.datetime.today().month
    df = df[df['lastLoginMonth']>=currentMonth-6]
    df = df[df['email'].notna()]
    df.to_sql('users', engine, if_exists='replace')


def downloadSellers(domainDB,engine):
    db = domainDB.sellers
    df_sellers = pd.DataFrame(columns=[\
        'userId','Email', 'CreatedDate', 'Enabled'])
    idx=0
    for doc in db.find({}, { \
        "_id": "$_id",
        "Email": "$Email",
        "CreatedDate": "$CreatedDate",
        "Enabled":"$Enabled"
            }).sort([('_id',pymongo.DESCENDING)]):
        idx+=1
        try:
            newRowDF = pd.DataFrame([[ \
                doc['_id'],doc['Email'],doc['CreatedDate'], doc['Enabled']\
                ]], columns=['userId','Email', 'CreatedDate','Enabled']\
                )
            df_sellers = df_sellers.append(newRowDF, ignore_index=True)
            if idx%10000==0:
                print(str(idx))
                df_sellers.to_sql('sellers', engine, if_exists='append')
                df_sellers = pd.DataFrame(columns=[ \
                    'userId', 'Email', 'CreatedDate', 'enabled'])
        except:
            print("Loading data error at line"+str(idx))
    df_sellers.to_sql('sellers', engine, if_exists='append')


def main():
    categoryDB, domainDB = connMongo.conn(sys.argv[1], sys.argv[2]) #pw_for_InvDB, pw_for_DomainDB
    engine = createDB()
    # downloadWishList(domainDB,engine)
    # downloadOrder(domainDB,engine)
    # downloadUsers(domainDB, engine)
    downloadItems(categoryDB, engine)


if __name__ == "__main__":
    main()
