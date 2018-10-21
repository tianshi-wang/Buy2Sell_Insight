import pandas as pd
import numpy as np
from syncAwsRDS import connAWS


def summary():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    engine = connAWS()
    sql_query = """
    SELECT * FROM summary ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df.iloc[:,:-1]


def collectionGroupbyModule():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    engine = connAWS()
    sql_query = """
    SELECT * FROM collectiongroupbymodule Limit 5    ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df


def inventoryLevel():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    engine = connAWS()
    sql_query = """
    SELECT * FROM inventorylevel Limit 10    ;
    """
    df = pd.read_sql_query(sql_query, engine)
    df = df.drop(['numinv', 'numwant'], axis=1)
    df = df.fillna(value=0)
    return df


def top3lowest():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    engine = connAWS()
    sql_query = """
    SELECT * FROM inventorylevel Limit 10
    """
    df = pd.read_sql_query(sql_query, engine)
    column = df.columns[-1]
    df = df.fillna(value=0)
    df = df.sort_values(by=column)
    return list(df.module[0:3])

def wishlistGroupbyModule():
    engine = connAWS()
    sql_query = """
    SELECT * FROM wishlistgroupbycategory Limit 5    ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df

def userTable(categories):
    if len(categories)==1:
        categories=(categories[0],'')
    engine = connAWS()
    sql_query = """
    with topusers as (
    select t1."userId", t1."weight", t2."likelihood", t1."weight"*t2."likelihood"*100 as score
    from(
        select "userId", sum("count")/avg("totalcoll") as weight
        from collectionbyuser
        where "ModuleName" in {}
        group by "userId"
        ) as t1
    join likelihood as t2 
    on t1."userId"=t2."userId"
    order by score DESC
    limit 100
    )
    
    select collectionbyuser.*, t2.weight, t2."likelihood",t2.score
    from collectionbyuser
    left join topusers as t2
    on collectionbyuser."userId"=t2."userId"
    where collectionbyuser."ModuleName" in {} and t2.score is not Null
    order by t2.score DESC
    limit 60
    """.format(tuple(categories), tuple(categories))
    df = pd.read_sql_query(sql_query, engine, index_col='userId')
    df['percent'] = df['count']/df['totalcoll']
    df
    df_left = df.pivot(columns='ModuleName',values='percent')
    df_left = df_left.fillna(value=0)
    result = df_left.join(df[['likelihood','score']]).sort_values(by='score', ascending=False)
    for column in result.columns:
        result[column]=result[column].map(lambda n: '{:.2f}'.format(n))
    result = result.reset_index()
    return result

userTable(('funko',''))

def ordersGroupbyCategory():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    engine = connAWS()
    sql_query = """
    SELECT * FROM ordersgroupbycategory Limit 5    ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df.iloc[:,:-1]

def users():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    engine = connAWS()
    sql_query = """
    SELECT * FROM users   ;
    """
    df = pd.read_sql_query(sql_query, engine)

    return df

def usercoll(categories=("""SELECT DISTINCT "ModuleName" FROM collectiongroupbyuserandmodule""")):
    engine = connAWS()
    sql_query = """
    SELECT *
    FROM collectiongroupbyuserandmodule
    WHERE "ModuleName" IN {:s}
    """.format(categories)
    df = pd.read_sql_query(sql_query, engine)
    return df


def collectionGroupby():
    engine = connAWS()
    """
    Read collections table and write new table collectiongroupby
    :return: format as "userId, moduleName, year, month, count"
    """
    # query:
    sql_query = """
    SELECT * FROM collectiongroupbymodule Limit 5
    ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df





