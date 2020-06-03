import time
import requests

from feed.services import fetch_posts
from feed.policy import TIME_BLOCK_SIZE

# test fetch_posts
now = int(time.time())
epoch = now - now % TIME_BLOCK_SIZE

before = time.time()
posts, hot_factors = fetch_posts(epoch, 'seattle')
after = time.time()

lat = int((after - before) * 1000)
num_posts_fetched = len(posts)

print(f'{len(posts)} posts fetched in {lat} ms:')
for i in range(len(posts)):
    print(f'  {posts[i]} hf: {hot_factors[i]}')

epoch -= TIME_BLOCK_SIZE
while num_posts_fetched < 300:
    before = time.time()
    posts, hot_factors = fetch_posts(epoch, 'seattle')
    after = time.time()

    lat = int((after - before) * 1000)
    print(f'{len(posts)} posts fetched in {lat} ms:')
    for i in range(len(posts)):
        print(f'  {posts[i]} hf: {hot_factors[i]}')

    num_posts_fetched += len(posts)
    epoch -= TIME_BLOCK_SIZE

# TODO: Test populate_posts_data

# r = requests.get('http://localhost:5000/ping')
# print(r.text)

# r = requests.get('http://localhost:5000/youn/seattle/feed')
# print(r.json())

