## Populates database with test data.

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

# used to generate random ages for posts
now = int(time.time())
time_ago = now - 86400*3 # s days

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

    creationTime = random.randint(week_ago, now)

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

def random_str(max_len):
    start = random.randint(0, len(dummy_text) - 1 - max_len) 
    length = random.randint(7, max_len)
    return dummy_text[start:start+length]

# insert cities
#for id, displayName in cities.items():
#    cursor.execute('INSERT INTO Locality VALUES (?,?)', id, displayName)
#cursor.commit()

# insert users
#city_ids = [key for key in cities.keys()]
#for user in users:
#    cursor.execute('INSERT INTO Users VALUES (?,?,?,?,?,?,?)', user.lower(),
#            random.choice(city_ids), user,
#            f'Hello! My name is {user}.', 1, time.time(), 'email')
#cursor.commit()

num_posts = dict()

# insert ~500 posts per user
cursor.execute('SELECT id, locality from Users')
rows = cursor.fetchall()
for row in rows:
    id, locality = row
    for i in range(500):
        post = new_random_post(id)
        # check if post with same key already exists
        cursor.execute('SELECT * from Posts where creator=? and creationTime=?',
                post['creator'], post['creationTime'])
        exists = cursor.fetchone()
        if not exists:
            cursor.execute('INSERT INTO Posts VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                    post['creator'], post['creationTime'], post['lat'],
                    post['lng'], locality, post['address'], post['mediaId'], post['title'],
                    post['description'], post['likes'], post['seenBy'])
            cursor.commit()
            num_posts[locality] = num_posts.get(locality, 0) + 1

print('database successfully populated!')
for locality, num in num_posts.items():
    print(f'  {locality}: {num} posts')

