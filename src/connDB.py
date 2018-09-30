
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

import psycopg2
import pandas as pd

def connDB():

    dbname = 'insightProj'
    username = 'Vera'  # change this to your username
    engine = create_engine('postgres://%s@localhost/%s' % (username, dbname))
    # print(engine.url)
    if not database_exists(engine.url):
        create_database(engine.url)
    # print(database_exists(engine.url))

    dbname = 'insightProj'
    username = 'Vera'  # change this to your username

    conn = None
    conn = psycopg2.connect(database=dbname, user=username)
    return engine, conn


def connAWS():
    dbname = 'birth_db'  # DB name not table
    username = 'Vera'  # change this to your username
    passwd = '111111aa'
    hostAddr = 'insightdb.c4f4cvkgxat9.us-east-2.rds.amazonaws.com:5432'
    awsEngine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (username, passwd, hostAddr, dbname))
    # print(awsEngine.url)
    if not database_exists(awsEngine.url):
        create_database(awsEngine.url)
    # print(database_exists(awsEngine.url))
    # print("Table names on AWS DB (self.tableNameAWS to access):")
    # tableNameAWS = awsEngine.table_names()
    # print(tableNameAWS)
    return awsEngine,awsEngine


def runQuery(sql_query):
    """
    Read collections table and write new table collectiongroupby
    :return: format as "userId, moduleName, year, month, count"
    """
    conn = connDB()
    # query:

    df = pd.read_sql_query(sql_query, conn)
    return df