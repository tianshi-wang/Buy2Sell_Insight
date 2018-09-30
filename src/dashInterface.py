import connMongo
import pymongo
import pandas as pd
from sqlalchemy import create_engine
from bson.son import SON
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import sklearn
import numpy as np
from connLocalDB import connAWS


def summary():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    _, engine = connAWS()
    sql_query = """
    SELECT * FROM summary ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df.iloc[:,:-1]

def collectionGroupbyModule():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    _, engine = connAWS()
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
    _, engine = connAWS()
    sql_query = """
    SELECT * FROM ordersgroupbycategory Limit 5    ;
    """
    df = pd.read_sql_query(sql_query, engine)
    return df.iloc[:,:-1]

def users():
    """
    :return: format as "userId, moduleName, year, month, count"
    """
    _, engine = connAWS()
    sql_query = """
    SELECT * FROM users     ;
    """
    df = pd.read_sql_query(sql_query, engine)

    return df

def collectionGroupby():
    _, engine = connAWS()
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





