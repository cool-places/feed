import time
import requests

from feed.services import fetch_posts, build_trees, get_feed_page, populate_posts_data
from feed.policy import TIME_BLOCK_SIZE
from feed.wtree import WTree, print_tree    

def test_fetch_posts():
    now = int(time.time())
    epoch = now - now % TIME_BLOCK_SIZE

    before = time.time()
    posts, hot_factors = fetch_posts(epoch, 'seattle')
    after = time.time()

    lat = int((after - before) * 1000)
    print(f'{len(posts)} posts fetched in {lat} ms:')

    epoch -= TIME_BLOCK_SIZE
    while num_posts_fetched < 300:
        before = time.time()
        posts, hot_factors = fetch_posts(epoch, 'seattle')
        after = time.time()

        lat = int((after - before) * 1000)
        print(f'{len(posts)} posts fetched in {lat} ms:')

        epoch -= TIME_BLOCK_SIZE

def test_grow_trees():
    before = time.time()
    lean, fat = WTree(), WTree()
    grow_trees('youn', 'seattle', lean, fat)
    after = time.time()

    print('lean:')
    print_tree(lean)
    print('fat:')
    print_tree(fat)

    lat = int((after - before) * 1000)
    print(f'{lean.size()} posts added to tree in {lat} ms:')

def test_build_trees():
    before = time.time()
    lean, fat = build_trees('youn', 'seattle')
    after = time.time()

    print('lean:')
    print_tree(lean)
    print('fat:')
    print_tree(fat)

    lat = int((after - before) * 1000)
    print(f'{lean.size()} posts added to tree in {lat} ms:')

def test_populate_posts_data():
    lean, fat = build_trees('youn', 'seattle')

    before = time.time() 
    page = populate_posts_data(get_feed_page('youn', lean, fat))
    after = time.time()

    print('page (25):')
    for post in page:
        print('likes:', post['likes'])
    lat = (after - before) * 1000
    print(f'posts populated in {lat} ms')

def test_endpoints():
    r = requests.get('http://localhost:5000/ping')
    print(r.text)

    r = requests.get('http://localhost:5000/youn/seattle/feed')
    print(r.json())


