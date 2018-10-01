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

def wishlistGroupbyModule():
    _, engine = connAWS()
    sql_query = """
    SELECT * FROM wishlistgroupbycategory Limit 5    ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df


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
    SELECT * FROM users     ;
    """
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





