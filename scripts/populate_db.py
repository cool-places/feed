## Populates database with test users and cities.

import random
import time
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

cities = {
    'seattle': 'Seattle, US',
    'seoul': 'Seoul, South Korea',
    'atlanta': 'Atlanta, US'
}

users = [
    'Akib',
    'Rubab',
    'Qin',
    'Chen Chen',
    'Anjana',
    'Choukri',
    'Steve',
    'Adrianna',
    'Tim',
    'Alok',
    'Reece',
    'Nikki',
    'Adam',
    'TJ'
]

# insert cities
for id, displayName in cities.items():
   cursor.execute('INSERT INTO Locality VALUES (?,?)', id, displayName)

# insert users
city_ids = [key for key in cities.keys()]
for user in users:
   cursor.execute('INSERT INTO Users VALUES (?,?,?,?,?,?,?)', user.lower(),
           random.choice(city_ids), user,
           f'Hello! My name is {user}.', 1, time.time(), 'email')
           
cursor.commit()
print('database successfully populated!')
