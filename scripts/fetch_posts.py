import time
import requests
import sys

page_size = int(sys.argv[1])

if (len(sys.argv) == 3):
    town = sys.argv[2]
else:
    town = 'NightCity'

before = time.time() 
r = requests.get(f'http://localhost:7191/1/feed?town={town}&page_size={page_size}&refresh=true')
posts = r.json()
lat = (time.time() - before) * 1000

print(f'returned {len(posts)} posts in {lat} ms')
for post in posts:
    print(post)
    # age = int((before - post['creationTime']/1000) / 3600)
    # print('  votes:', post['votes'], 'age:', f'{age}h', 'voted:', post['voted'], 'created by:', post['creatorUsername'])