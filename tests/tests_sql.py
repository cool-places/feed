import configparser
import pyodbc

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

cursor.execute('SELECT * from Posts where creator=?', 'rubab')
row = cursor.fetchone()
# test whether row can get converted
# to dict out of the box (it doesn't)
print(dict(row))