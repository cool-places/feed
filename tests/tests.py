import time
import requests

from feed.services import fetch_posts, build_trees, get_feed_page, populate_posts_data
from feed.policy import TIME_BLOCK_SIZE
from feed.wtree import WTree, print_tree

# test fetch_posts
now = int(time.time())
epoch = now - now % TIME_BLOCK_SIZE

before = time.time()
posts, hot_factors = fetch_posts(epoch, 'seattle')
after = time.time()

lat = int((after - before) * 1000)
num_posts_fetched = len(posts)

print(f'{len(posts)} posts fetched in {lat} ms:')
#for i in range(len(posts)):
#    print(f'  {posts[i]} hf: {hot_factors[i]}')

epoch -= TIME_BLOCK_SIZE
while num_posts_fetched < 300:
    before = time.time()
    posts, hot_factors = fetch_posts(epoch, 'seattle')
    after = time.time()

    lat = int((after - before) * 1000)
    print(f'{len(posts)} posts fetched in {lat} ms:')
    #for i in range(len(posts)):
    #    print(f'  {posts[i]} hf: {hot_factors[i]}')

    num_posts_fetched += len(posts)
    epoch -= TIME_BLOCK_SIZE

# test grow trees
#lean = WTree()
#fat = WTree()
#grow_trees('youn', 'seattle', lean, fat)

lean, fat = build_trees('youn', 'seattle')

#print('lean:')
#print_tree(lean)
#print('fat:')
#print_tree(fat)

before = time.time()
page = populate_posts_data(get_feed_page('youn', lean, fat))
after = time.time()

print('page (25):')
for post in page:
    print('likes:', post['likes'])
lat = (after - before) * 1000
print(f'took {lat} ms')

# TODO: Test populate_posts_data

# r = requests.get('http://localhost:5000/ping')
# print(r.text)

# r = requests.get('http://localhost:5000/youn/seattle/feed')
# print(r.json())

