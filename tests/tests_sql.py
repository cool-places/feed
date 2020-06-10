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

def snap_to_grid(location):
    lat = int(location[0]*10000)
    r = lat % 2500
    lat -= r
    if (r >= 1250):
        lat += 2500
    location[0] = lat / 10000.0

    lng = int(location[1]*10000)
    r = lng % 2500
    lng -= r
    if (r >= 1250):
        lng += 2500
    location[1] = lng / 10000.0

p = [47.25, -122.6458]
snap_to_grid(p)
print(p)

# query = """
# declare @p geography = geography::Point(?, ?, 4326);
# select creator, creationTime, location.Lat, location.Long from Posts where location.STDistance(@p) <= ? and creationTime between ? and ?;
# """
# cursor.execute(query, 47.0, -122.0, 60000, 0, 10000)
# row = cursor.fetchone()
# print(row)