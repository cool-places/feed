import time
import requests

from services import fetch_posts

# //Test fetch_posts
now = int(time.time())
epoch = now - now % TIME_BLOCK_SIZE

before = time.time()
posts, hot_factors = fetch_posts(epoch, 'seattle')
after = time.time()

print(f'{len(posts)} posts fetched:')

for i in range(len(posts)):
    print(f'  {posts[i]} hf: {hot_factors[i]}')

lat = int((after - before) * 1000)
print(f'took {lat} ms')

# TODO: Test populate_posts_data

# r = requests.get('http://localhost:5000/ping')
# print(r.text)

# r = requests.get('http://localhost:5000/youn/seattle/feed')
# print(r.json())

