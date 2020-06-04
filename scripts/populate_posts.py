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

arg1 = sys.argv[1]
t = int(arg1[:-1])
unit = arg1[-1]

if unit == 'h':
    time_ago = now - (3600)*t
else: # 'd'
    time_ago = now - (24*3600)*t

num_posts = int(sys.argv[2])

# used to generate random strings
dummy_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit,\
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris\
        nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in\
        reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.\
        Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt\
        mollit anim id est laborum.'

def new_random_post(creator, locality):
    # mean of 0.2
    hot_factor = max(abs(random.gauss(0.2, 0.15)), 1)
    # mean of 50
    seen = int(abs(random.expovariate(1/50)))
    likes = int(seen * hot_factor)
    creationTime = random.randint(time_ago, now)

    return (
        creator,
        creationTime,
        random.uniform(0, 90),
        random.uniform(0, 180),
        locality,
        random_str(32),
        'some-id',
        random_str(24),
        random_str(100),
        likes,
        seen
    )

def random_str(max_len):
    start = random.randint(0, len(dummy_text) - 1 - max_len) 
    length = random.randint(7, max_len)
    return dummy_text[start:start+length]

before = time.time()

inputs = []
# collect users
cursor.execute('SELECT id, locality from Users')
users = cursor.fetchall()

cursor.fast_executemany = True
added = 0
new_posts = {}
for i in range(num_posts):
    user_id, locality = random.choice(users)
    post = new_random_post(user_id, locality)
    # check if post with same key already exists
    cursor.execute('SELECT * from Posts where creator=? and creationTime=?',
        post[0], post[1])
    exists = cursor.fetchone()
    if not exists and (post[0], post[1]) not in new_posts:
        inputs.append(post)
        new_posts.add((post[0], post[1]))
        added += 1

cursor.executemany('INSERT INTO Posts VALUES (?,?,?,?,?,?,?,?,?,?,?)', inputs)
cursor.commit()

after = time.time()

lat = after - before
print(f'{added} posts added in {lat} s')




