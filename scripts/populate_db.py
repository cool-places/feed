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

cities = ['Seattle', 'Seoul', 'Atlanta']

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

# insert users
for user in users:
   cursor.execute('INSERT INTO Users VALUES (?,?,?,?,?,?,?)',
           random.choice(cities), user,
           f'Hello! My name is {user}.', 1, int(time.time() * 1000), 'email')
           
cursor.commit()
print('database successfully populated!')
