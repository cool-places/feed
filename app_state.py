## Store global variables (such as DB and redis connection) here.

import configparser
import pyodbc
import redis

config = configparser.ConfigParser()
config.read('./app.ini')

server = config['db']['server'] # FQDN
database = config['db']['database'] # database name
username = config['db']['username']
password = config['db']['password']
driver = '{ODBC Driver 17 for SQL Server}'

# what does cnxn stand for?
cnxn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
cursor = cnxn.cursor()

r = redis.Redis(host=config['redis']['host'], port=6379, db=0)
