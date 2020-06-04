## Populates DB with test posts

import random
import time
import configparser
import pyodbc
import sys

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

# used to generate random ages for posts
now = int(time.time())

arg = sys.argv[1]
t = int(arg[:-1])
unit = arg[-1]

if unit == 'h':
    time_ago = now - (3600)*t
else: # 'd'
    time_ago = now - (24*3600)*t

# used to generate random strings
dummy_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit,\
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris\
        nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in\
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt\
        mollit anim id est laborum.'

# Note that "hot" posts are
# relatively rare (just like the real world)
hot_factors = [0.01, 0.22, 0.3, 0.35, 0.4, 0.6, 0.74]
cum_hot_weights = [60, 70, 80, 85, 90, 97, 100]

seen_vals = [10, 100, 1000, 5000, 10000]
cum_seen_weights = [10000, 15000, 16000, 16100, 16110]

def new_random_post(creator):
    hot_factor =  random.choices(hot_factors, cum_weights=cum_hot_weights)[0]
    seen = random.choices(seen_vals, cum_weights=cum_seen_weights)[0]
    likes = int(seen * hot_factor)

    likes = random.randint(max(0, likes-10), min(seen, likes+10))

    creationTime = random.randint(time_ago, now)

    return {
        'creator': creator,
        'creationTime': creationTime,
        'lat': random.uniform(0, 90),
        'lng': random.uniform(0, 180),
        'address': random_str(32),
        'mediaId': 'some-url',
        'title': random_str(24),
        'description': random_str(100),
        'likes': likes,
        'seenBy': seen
    }