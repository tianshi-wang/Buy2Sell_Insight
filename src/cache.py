"""
Query real-time SQL data, and store dashboard-related data to refresh-updated SQL tables.
1. writeCollectionGroupbyModule: TABLE collectiongroupbymodule [module, month1, month2, ...]
"""

import pandas as pd
import numpy as np
from connLocalDB import connDB
from datetime import datetime, timedelta

def groupby_pivot(df,rowIdx, colIdx, val):
    """
    Process a dateframe like:
    user Month Item
    John Dec   item1
    John Dec   item2
    Andy Jan   item2
    To a DF like:
    user Jan ... Dec
    john  0  ... 2
    Andy  1  ... 0
    Params: row index (rowIdx), columns (colIdx), value is count(val) for a given rowIdx and colIdx
    """
    df_series = df.groupby([rowIdx,colIdx])[val].count()
    df_groupby = df_series.to_frame()
    df_groupby.reset_index(inplace=True)
    df_groupby_pivoted = df_groupby.pivot(index=rowIdx, columns=colIdx, values=val).fillna(value=0)
    return df_groupby_pivoted

def userClean():
    engine, conn = connDB()
    sql_query = """
    SELECT * FROM users
    ;
    """

    df = pd.read_sql_query(sql_query, conn)
    print(df.head())
    df['month'] = df['CreatedDate'].apply(lambda x: (x.year-2017)*12+x.month)
    df = df.drop(['CreatedDate'], axis=1)
    df.to_sql('users', engine, if_exists='replace')
    print("UserClean done!")


def writeSummary():
    engine,conn = connDB()

    # write collection summary
    collections_number_query = """
    select * from collectiongroupbymodule;
    """
    df_collections = pd.read_sql_query(collections_number_query, conn)
    df_collections = df_collections.sum(axis=0)
    df_collections = [int(x/1000) for x in list(df_collections)[-13:-1]]

    # write order summary
    order_number_query = """
    select * from orders;
    """
    df_orders = pd.read_sql_query(order_number_query, conn)
    df_orders['month'] = df_orders['created_date'].apply(lambda x: (x.year-2017)*12+x.month)
    df_orders = list(df_orders.groupby(['month'])['userId'].count())[-12:]
    df_orders = [x for x in list(df_orders)[-13:-1]]

    wishlist_query="""
    select * from wishlistgroupbycategory;
    """
    df_wishlist = pd.read_sql_query(wishlist_query, conn)
    df_wishlist = df_wishlist.sum(axis=0)
    df_wishlist = [int(x/1000) for x in list(df_wishlist)[-13:-1]]

    #write user summary
    user_number_query = """
    SELECT * FROM users;
    """
    df_user = pd.read_sql_query(user_number_query, conn)
    user_groupby=df_user.groupby(['month'])['userId'].count()
    df_user = [int(x/1000) for x in list(user_groupby)[-12:]]

    # write seller summary
    seller_number_query = """
    SELECT * FROM sellers;
    """
    df_seller = pd.read_sql_query(seller_number_query, conn)
    df_seller['month'] = df_seller['CreatedDate'].apply(lambda x: (x.year-2017)*12+x.month)
    df_seller = df_seller.groupby(['month'])['userId'].count()
    monthList = list(df_seller.index)[-12:]
    df_seller = list(df_seller)[-12:]

    df_summary = pd.DataFrame.from_dict({'NumberOfOrders':df_orders, 'NumberOfCollections':df_collections, \
                                         'NumberOfWishlist':df_wishlist, 'NumberOfUsers':df_user, \
                                         'NumberOfSellers':df_seller, }, orient='index',columns=monthList)
    df_summary.to_sql('summary', engine, if_exists='replace')

def writeCollectionByUser():
    engine, conn = connDB()
    sql_query = """
      SELECT collections."userId", collections.module, collections."itemId", items."CategoryName"
      FROM collections
      JOIN items ON collections."itemId" = items."itemId"
      WHERE collections.created_date > '%s'::date
      """ % str(datetime.now().date()-timedelta(days=90))
    df_users = pd.read_sql_query(sql_query, conn)

    user_module = groupby_pivot(df_users, rowIdx='userId', colIdx='module', val='itemId')
    user_category = groupby_pivot(df_users, rowIdx='userId', colIdx='CategoryName', val='itemId')



    user_module['ratio'] = user_module.max(axis=1)/user_module.sum(axis=1)
    user_category['ratio'] = user_category.max(axis=1)/user_category.sum(axis=1)


    user_module.to_sql('collectiongroupbyuserandmodule', engine, if_exists='replace', index=False)
    user_category.to_sql('collectiongroupbyuserandcategory', engine, if_exists='replace', index=False)


def writeWishlistGroupby():
    """
      Write three tables: order_groupby_userId, order_groupby_category
      (userId and catergary as index, month as columns)
      """
    engine, conn = connDB()
    sql_query = """
      SELECT "userId", created_date, category, "itemId" FROM wishlist
      WHERE created_date >= '2017-09-01'::date
      """
    df = pd.read_sql_query(sql_query, conn)
    df['month'] = df['created_date'].apply(lambda x: (x.year - 2017) * 12 + x.month)  # "added month index 2017-01 as 1"
    df = df.drop(['created_date'], axis=1)
    df_series = df.groupby(['category', 'month'])['itemId'].count()
    df_groupbyCategory = df_series.to_frame()
    df_groupbyCategory.reset_index(inplace=True)
    df_groupbyCategory = df_groupbyCategory.rename(columns={'itemId': 'numWishlist'})
    df_groupbyCategory_pivoted = df_groupbyCategory.pivot(index='category', columns='month',
                                                          values='numWishlist').fillna(value=0)
    df_groupbyCategory_pivoted['sum'] = df_groupbyCategory_pivoted.sum(axis=1)
    df_groupbyCategory_pivoted = df_groupbyCategory_pivoted.sort_values(['sum'], ascending=False)
    df_groupbyCategory_pivoted = df_groupbyCategory_pivoted.drop('sum',axis=1)
    df_groupbyCategory_pivoted.to_sql('wishlistgroupbycategory', engine, if_exists='replace')

    df_series = df.groupby(['userId', 'month'])['itemId'].count()
    df_groupbyUser = df_series.to_frame()
    df_groupbyUser.reset_index(inplace=True)

    df_groupbyUser = df_groupbyUser.rename(columns={'itemId': 'numWishlist',})
    df_groupbyUser_num = df_groupbyUser.pivot(index='userId', columns='month', values='numWishlist').fillna(value=0)
    df_groupbyUser_num.reset_index(inplace=True)
    df_groupbyUser_num.columns = ['userId']+['{:02d}'.format(int(x))+'-numWishlist' for x in df_groupbyUser_num.columns[1:]]
    df_groupbyUser_num.to_sql('wishlistsgroupbyusersnum', engine, if_exists='replace')



def writeOrderGroupby():
    """
    Write three tables: order_groupby_userId, order_groupby_category
    (userId and catergary as index, month as columns)
    """
    engine,conn = connDB()
    sql_query = """
    SELECT orders.*, items."CategoryName" FROM orders
    LEFT JOIN items
    ON orders.item_id=items."itemId";
    """
    df = pd.read_sql_query(sql_query, conn)
    df['month'] = df['created_date'].apply(lambda x: (x.year-2017)*12+x.month) #"added month index 2017-01 as 1"
    df = df.drop(['created_date'], axis=1)
    df_series = df.groupby(['CategoryName','month'])['order_id'].count()
    df_groupbyCategory = df_series.to_frame()
    df_groupbyCategory.reset_index(inplace=True)
    df_groupbyCategory = df_groupbyCategory.rename(columns={'order_id': 'numOrders'})
    df_groupbyCategory_pivoted = df_groupbyCategory.pivot(index='CategoryName',columns='month',values='numOrders').fillna(value=0)
    df_groupbyCategory_pivoted['sum'] = df_groupbyCategory_pivoted.sum(axis=1)
    df_groupbyCategory_pivoted = df_groupbyCategory_pivoted.sort_values(['sum'],ascending=False)
    df_groupbyCategory_pivoted.to_sql('ordersgroupbycategory', engine, if_exists='replace')

    df_groupbyUser = df.groupby(['userId','month'])['Amount'].agg(['sum','count'])
    df_groupbyUser.reset_index(inplace=True)
    df_groupbyUser = df_groupbyUser.rename(columns={'sum': 'amount', 'count':'numOrders'})
    df_groupbyUser_numOrders = df_groupbyUser.pivot(index='userId',columns='month',values='numOrders').fillna(value=0)
    df_groupbyUser_amount = df_groupbyUser.pivot(index='userId',columns='month',values='amount').fillna(value=0)
    df_groupbyUser_numOrders.reset_index(inplace=True)
    df_groupbyUser_amount.reset_index(inplace=True)

    df_groupbyUser_numOrders.columns = ['userId']+['{:02d}'.format(int(x))+'-numOrders' for x in df_groupbyUser_numOrders.columns[1:]]
    df_groupbyUser_amount.columns = ['userId']+['{:02d}'.format(int(x))+'-amount' for x in df_groupbyUser_amount.columns[1:]]
    df_groupbyUser_numOrders.to_sql('ordersgroupbyusersnum', engine, if_exists='replace')
    df_groupbyUser_amount.to_sql('ordersgroupbyusersamount', engine, if_exists='replace')



def writeCollectionGroupbyModule():
    engine,conn = connDB()
    """
    Read collections table and write new table collectiongroupby
    :return: format as "userId, moduleName, year, month, count"
    """
    # query:
    sql_query = """
    SELECT * FROM collection
    ;
    """
    df = pd.read_sql_query(sql_query, conn)

    df['month'] = df['created_date'].apply(lambda x: (x.year-2017)*12+x.month) #"added month index 2017-01 as 1"
    df = df.drop(['created_date'], axis=1)
    df_series = df.groupby(['module', 'month'])['itemId'].count()
    df = df_series.to_frame()
    df.reset_index(inplace=True)
    df = df.rename(columns={'itemId': 'numCollections'})
    df_pivoted = df.pivot(index='module',columns='month',values='numCollections').fillna(value=0)
    df_pivoted['sum'] = df_pivoted.sum(axis=1)
    df_pivoted = df_pivoted.sort_values(['sum'],ascending=False)
    df_pivoted.to_sql('collectiongroupbymodule', engine, if_exists='replace')


def writeCollectionGroupbyUserAndModule():
    engine, conn = connDB()
    """
    Read collections table and write new table collectiongroupby
    :return: format as "userId, moduleName, year, month, count"
    """
    # query:
    sql_query = """
    SELECT created_date, "userId", "itemId", module  
    FROM collection
    WHERE created_date >= '2018-01-01'::date
    ;
    """
    df = pd.read_sql_query(sql_query, conn)

    df['month'] = df['created_date'].apply(lambda x: '{:02.0f}'.format((x.year-2017)*12+x.month)+'-') #"added month index 2017-01 as 1"
    df['monthModule']=df[['month', 'module']].apply(lambda x: ''.join(x), axis=1)
    df = df.drop(['created_date', 'month'], axis=1)

    df_series = df.groupby(['userId', 'monthModule'])['itemId'].count()
    df = df_series.to_frame()
    df.reset_index(inplace=True)
    df = df.rename(columns={'itemId': 'numCollections'})
    df_pivoted = df.pivot(index='userId',columns='monthModule',values='numCollections').fillna(value=0)
    df_pivoted['sum'] = df_pivoted.sum(axis=1)

    df_pivoted = df_pivoted.sort_values(['sum'],ascending=False)
    df_pivoted = df_pivoted[df_pivoted['sum']>10]
    df_pivoted = df_pivoted.drop('sum', axis=1)
    df_pivoted.to_sql('collectiongroupbyuserandmodule', engine, if_exists='replace')
    print("Wrote to collectiongroupbyuserandmodule")


def writeFeatures():
    """
    Write features. The users are active users.
    Feature time dated to last 12 months.
    :return:
    """
    engine, conn = connDB()
    feature_query = """
        SELECT collectiongroupbyuserandmodule.*, sellers."CreatedDate" AS sellerCreatedDate, 
        ordersgroupbyusersamount.*, ordersgroupbyusersnum.*, wishlistsgroupbyusersnum.*
        FROM collectiongroupbyuserandmodule
        INNER JOIN users ON collectiongroupbyuserandmodule."userId"=users."userId"
        LEFT JOIN sellers ON users."email"=sellers."Email"
        LEFT JOIN ordersgroupbyusersamount on collectiongroupbyuserandmodule."userId"=ordersgroupbyusersamount."userId"
        LEFT JOIN ordersgroupbyusersnum on collectiongroupbyuserandmodule."userId"=ordersgroupbyusersnum."userId"
        LEFT JOIN wishlistsgroupbyusersnum on collectiongroupbyuserandmodule."userId" = wishlistsgroupbyusersnum."userId"      
        ;
    """
    df_features = pd.read_sql_query(feature_query, conn)
    df_features['month'] = df_features['sellercreateddate'].apply(lambda x: (x.year-2017)*12+x.month).fillna(value=0)
    df_features['month'] = df_features['month'].apply(lambda x: int(x))
    df_features = df_features.drop(['userId','sellercreateddate'],axis=1)
    df_features = df_features.fillna(value=0)


    months = list(set([ x[:2] for x in df_features.columns[:-1]]))  # last column is sellerCreationMonth
    startingMonth= int(df_features.columns[0][0:2])
    endMonth = int(df_features.columns[-2][0:2])

    topCategories_query = """
    select * from collectiongroupbymodule
    """
    categories = list(pd.read_sql_query(topCategories_query, conn)['module'])[:20]
    allColumns = [str(x)+'-'+str(y) for x in months for y in categories]
    allColumns.append('selling')

    featuresFillEmptyColumn = pd.DataFrame(columns=allColumns).fillna(value=0)
    for column in allColumns:
        try:
            featuresFillEmptyColumn[column] = df_features[column]
        except:
            pass
    featuresFillEmptyColumn = featuresFillEmptyColumn.fillna(value=0)
    featureColumns = [x+y for x in ['t-3-','t-2-','t-1-'] for y in categories]+['t-3-numOrders','t-2-numOrders','t-1-numOrders']+ \
                     ['t-3-amount', 't-2-amount', 't-1-amount']+['t-3-wishlist', 't-2-wishlist', 't-1-wishlist']
    featureColumns.append('selling')
    features = pd.DataFrame(columns=featureColumns)
    for rowidx in range(df_features.shape[0]):
        sellingMonth = int(df_features.iloc[rowidx, -1])
        t = sellingMonth
        if sellingMonth>15:    # Only consider t>2018/03
            # for idx in range(min(3,t-15)):
            end = t
            orderColumn = ['{:02d}'.format(x) + '-numOrders' for x in range(end-3,end)]+\
                            ['{:02d}'.format(x) + '-amount' for x in range(end-3,end)]+ \
                          ['{:02d}'.format(x) + '-numWishlist' for x in range(end-3,end)]
            newRowValue = list(featuresFillEmptyColumn.iloc[rowidx, (end - startingMonth - 3) * len(categories): \
                                                        (end - startingMonth) * len(categories)])+\
                          list(df_features.iloc[rowidx][orderColumn])
            newRowValue.append(1)
            newRowDF = pd.DataFrame([newRowValue], columns=featureColumns)
            features = features.append(newRowDF,ignore_index=True)
        else:
            t = endMonth
            while t>15:
                orderColumn = ['{:02d}'.format(x) + '-numOrders' for x in range(t - 3, t)] + \
                              ['{:02d}'.format(x) + '-amount' for x in range(t - 3, t)]+\
                                ['{:02d}'.format(x) + '-numWishlist' for x in range(t - 3, t)]
                newRowValue = list(featuresFillEmptyColumn.iloc[rowidx, (t - startingMonth - 3) * len(categories): \
                                                            (t - startingMonth) * len(categories)])+ \
                              list(df_features.iloc[rowidx, :][orderColumn])
                newRowValue.append(0)
                newRowDF = pd.DataFrame([newRowValue], columns=featureColumns)
                features = features.append(newRowDF,ignore_index=True)
                t -= 1
        print(rowidx)
        if rowidx==100:
            print(rowidx)
    features.to_sql('features', engine, if_exists='replace')


def main():
    # Cache module write SQL tables for updating dashboard and model training.
    # Cache doesn't return anything; it only writes to SQL
    # dataIngestion module read the cache SQL and return DF for plot in Dashboard.
    # writeOrderGroupby()
    # writeCollectionGroupbyUserAndModule()
    writeCollectionByUser()
    # writeSummary()
    # writeWishlistGroupby()
    # writeFeatures()
    # writeCollectionGroupbyModule()
    # writeCollectionGroupbyUserAndModule()


if __name__ == "__main__":
    main()