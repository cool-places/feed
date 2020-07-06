## DB layer

import logging
import time
import pyodbc

from app_state import config

server = config['db']['server'] # FQDN
database = config['db']['database'] # database name
username = config['db']['username']
password = config['db']['password']
driver = '{ODBC Driver 17 for SQL Server}'

# what does cnxn stand for?
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()

def execute_sql(statement, retry, *args):
    global cnxn
    global cursor

    tried = 0
    while (tried != retry):
        try:
            cursor.execute(statement, *args)
            return
        except Exception as e:
            logging.error(e)
            logging.error('retrying to connect to SQL Server in 1 sec...')
            cursor.close()
            cnxn.close()
            time.sleep(1)
            
            cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
            cursor = cnxn.cursor()
            tried += 1

            if tried == retry:
                raise e