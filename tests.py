import time
import requests

from services import fetch_posts, grow_trees, \
build_trees, get_feed_page, populate_posts_data, \
fan_out
from policy import TIME_BLOCK_SIZE, INCEPTION
from wtree import WTree, print_tree    

MY_LOCATION = [47.6028, -122.3292] 

def test_fetch_posts():
    now = int(time.time() * 1000)
    epoch = now - now % TIME_BLOCK_SIZE

    before = time.time()
    posts, hot_factors = fetch_posts(epoch, MY_LOCATION)
    after = time.time()

    lat = int((after - before) * 1000)
    print(f'{len(posts)} posts fetched in {lat} ms')

    num_posts_fetched = len(posts)
    epoch -= TIME_BLOCK_SIZE
    while num_posts_fetched < 300:
        before = time.time()
        posts, hot_factors = fetch_posts(epoch, MY_LOCATION)
        after = time.time()

        lat = int((after - before) * 1000)
        print(f'{len(posts)} posts fetched in {lat} ms')

        epoch -= TIME_BLOCK_SIZE
        num_posts_fetched += len(posts)

def test_grow_trees():
    before = time.time()
    lean, fat = WTree(), WTree()
    grow_trees('youn', MY_LOCATION, lean, fat)
    after = time.time()

    print('lean:')
    print_tree(lean)
    print('fat:')
    print_tree(fat)

    lat = int((after - before) * 1000)
    print(f'{lean.size()} posts added to tree in {lat} ms:')

def test_build_trees():
    before = time.time()
    lean, fat = build_trees('youn', MY_LOCATION)
    after = time.time()

    print('lean:')
    print_tree(lean)
    print('fat:')
    print_tree(fat)

    lat = int((after - before) * 1000)
    print(f'{lean.size()} posts added to tree in {lat} ms:')

def test_populate_posts_data():
    lean, fat = build_trees('youn', MY_LOCATION)

    before = time.time() 
    page = populate_posts_data(get_feed_page('youn', lean, fat))
    after = time.time()

    print('page (25):')
    for post in page:
        age = int((after - post['creationTime']/1000) / 3600)
        print('likes:', post['likes'], 'age:', age, 'lat:', post['lat'], 'lng:', post['lng'])
    lat = (after - before) * 1000
    print(f'posts populated in {lat} ms')

def test_fan_out():
    now = int(time.time() * 1000)
    epoch = now - now % TIME_BLOCK_SIZE
    print('epoch:', epoch)

    points = fan_out(MY_LOCATION, 'new-post')
    print(len(points))
    for p in points:
        print(p)

def test_endpoints():
    r = requests.get('http://localhost:5000/ping')
    print(r.text)

    r = requests.get(f'http://localhost:5000/youn/feed?latlng={MY_LOCATION[0]},{MY_LOCATION[1]}')
    print(r.json())

    r = requests.get(f'http://localhost:5000/fanout?latlng={MY_LOCATION[0]},{MY_LOCATION[1]}&post_id=newpost')
    print(r.text)

test_endpoints()
