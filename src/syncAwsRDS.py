from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import sys

"""
This module copy tabels from local Postgresql to AWS RDS Postgresql
Local DB name: insightProj
AWS Instance Name: insightdb, AWS DB name: birth_db
"""


def connAWS():
    dbname = 'birth_db'  # DB name not table
    username = 'Vera'  # change this to your username
    passwd = '111111aa'
    hostAddr = 'insightdb.c4f4cvkgxat9.us-east-2.rds.amazonaws.com:5432'
    awsEngine = create_engine('postgresql+psycopg2://%s:%s@%s/%s' % (username, passwd, hostAddr, dbname))
    if not database_exists(awsEngine.url):
        create_database(awsEngine.url)
    return awsEngine


class LocalToAWS():
    def __init__(self):
        self.df=None
        self.dfList=None
        self.tableName=None

    def connAWS(self):
        self.awsEngine = connAWS()

    def connLocalDB(self):
        dbname = 'insightProj'
        username = 'Vera'  # change this to your username
        self.localEngine = create_engine('postgres://%s@localhost/%s' % (username, dbname))

    def migrateTables(self, tableToMove):
        def migrateOneTable(table):
            sql_query = "SELECT * FROM %s LIMIT 1000" % (table)
            df_table = pd.read_sql_query(sql_query, con=self.localEngine)
            df_table.to_sql(name=table, con=self.awsEngine, if_exists='replace', index=False)
            print("Finished " + table + "...")

        if type(tableToMove)==str:
            migrateOneTable(tableToMove)
        else:
            for table in tableToMove:
                migrateOneTable(table)


def main():
    """
    Copy selected tables stored on local PostgreSQL to AWS RDS
    The selected tables are listed in "tabelToMove"
    """
    writeAWS = LocalToAWS()
    writeAWS.connAWS()
    writeAWS.connLocalDB()
    print("Table names on local DB (self.tableNameLocal to access):")
    writeAWS.tableNameLocal = writeAWS.localEngine.table_names()
    print(writeAWS.tableNameLocal)

    print("Table names on AWS DB (self.tableNameAWS to access):")
    writeAWS.tableNameAWS = writeAWS.awsEngine.table_names()
    print(writeAWS.tableNameAWS)

    tableToMove = ['wishlistsgroupbyusersnum',
                   'wishlistgroupbycategory',
                   'features',
                   'orders',
                   'ordersgroupbycategory',
                   'ordersgroupbyusersnum',
                   'ordersgroupbyusersamount',
                   'collectiongroupbymodule',
                   'collectiongroupby',
                   'summary',
                   'collectiongroupbyuserandmodule',
                   ]
    writeAWS.migrateTables(tableToMove)


if __name__ == "__main__":
    main()