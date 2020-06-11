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

query = """
declare @p geography = geography::Point(?, ?, 4326);
select creator, creationTime, location.Lat, location.Long from Posts where location.STDistance(@p) <= ? and creationTime between ? and ?;
"""
cursor.execute(query, 47.0, -122.0, 60000, 0, 10000)
row = cursor.fetchone()
print(row)