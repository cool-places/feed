## DB layer

import logging
import time
import pyodbc
import redis

from app_state import config

server = config['db']['server'] # FQDN
database = config['db']['database'] # database name
username = config['db']['username']
password = config['db']['password']
driver = '{ODBC Driver 17 for SQL Server}'

## Singleton wrapper around pyodbc.cursor
##
## Handles retry logic and reonnects to SQL Server
## when connection is lost.
class DBCursor(object):
    NUM_TRIES = 3

    def __init__(self):
        self.connect()

    def connect(self):
        self.cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        self.cursor = self.cnxn.cursor()

    def close(self):
        self.cursor.close()
        self.cnxn.close()

    def execute(self, statement, *args):
        tried = 0
        while (tried != DBCursor.NUM_TRIES):
            try:
                self.cursor.execute(statement, *args)
                return
            except Exception as e:
                logging.error(e)
                logging.error('retrying to connect to SQL Server in 1 sec...')

                self.close()
                time.sleep(1)
                self.connect()
                
                tried += 1

                if tried == DBCursor.NUM_TRIES:
                    raise e

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

cursor = DBCursor()
r = redis.Redis(host=config['redis']['host'], port=6379, db=0)