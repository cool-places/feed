## Service layer. Exists to decouple application logic from HTTP context.
##
## Majority of the logic involves fetching things from DB and caching the
## results.

import time
import random
import json

from .wtree import WTree
from .app_state import cursor, cnxn, r
from .policy import TIME_BLOCK_SIZE, MAX_SEEN_POSTS, MIN_TREE_SIZE, PAGE_SIZE, FAT_PERCENT, HOT_FACTOR_EXPIRATION, calculate_hot_factor, is_cold

## Break down a post id into its composite key components.
def unpack(id):
    keys = id.split(b'_')
    keys[0] = keys[0].decode('utf-8')
    keys[1] = int(keys[1])
    return keys

## Calculate hot factors of posts in batches.
def calculate_hot_factors_batch(posts, hot_factors):
    # posts at these indices don't have hot factors
    # in cache (expired or never calculated)
    indices = []
    p = r.pipeline()

    for i in range(len(posts)):
        post = posts[i]
        if hot_factors[i] is None:
            indices.append(i)
            p.get(f'post:{post}:likes')
            p.get(f'post:{post}:seen_by')

    stats = p.execute()
    inputs = []
    for i in range(0, len(stats), 2):
        post = posts[indices[i//2]]
        keys = unpack(post)

        # if likes doesn't exist, seen_by also doesn't.
        # (and conversely (or is it inversely?) if likes exist,
        # so does seen_by).
        if stats[i] is None:
            # kinda bothers me to have to go back and forth to DB
            # for every post...but hopefully there aren't that
            # many posts whose stats are not cached
            cursor.execute('SELECT likes, seenBy FROM Posts\
                    WHERE creator=? AND creationTime=?')
            row = cursor.fetchone()
            stats[i], stats[i+1] = row[0], row[1]
            p.set(f'post:{post}:likes', row[0])
            p.set(f'post:{post}:seen_by', row[1])

        hf = calculate_hot_factor(keys[1], stats[i], stats[i+1])
        hot_factors[indices[i//2]] = hf

        p.set(f'post:{post}:hot_factor', hf)
        # force app to recalculate hot factor
        p.expire(f'post:{post}:hot_factor', HOT_FACTOR_EXPIRATION)

    p.execute()

## Fetch all posts in epoch at locality.
##
## If cache is True, caches data fetched
## from DB.
def fetch_posts(epoch, locality, cache=True):
    p = r.pipeline()
    posts = r.smembers(f'posts:{locality}:{epoch}')
    hot_factors = []

    if len(posts) != 0:
        # posts is a set in redis cache. This is
        # to (naively) support concurrent caching of posts
        # without worrying about duplicate posts
        posts = list(posts)
        for i in range(len(posts)):
            p.get(f'post:{posts[i]}:hot_factor')

        hot_factors = p.execute()
        calculate_hot_factors_batch(posts, hot_factors)
        return (posts, hot_factors)

    posts = []
    cursor.execute('SELECT creator, creationTime, likes, seenBy\
            FROM Posts\
            WHERE locality=?\
            AND creationTime BETWEEN ? AND ?',
            locality, epoch, epoch + TIME_BLOCK_SIZE - 1)
    
    row = cursor.fetchone()
    while row:
        post_id = f'{row[0]}_{row[1]}'
        posts.append(post_id)

        hf = calculate_hot_factor(row[1], row[2], row[3])
        hot_factors.append(hf)

        if cache:
            p.set(f'post:{post_id}:likes', row[2])
            p.set(f'post:{post_id}:seen_by', row[3])
            p.set(f'post:{post_id}:hot_factor', hf)
            # force app to recalculate hot factor after 60 seconds
            p.expire(f'post:{post_id}:hot_factor', 60)

        row = cursor.fetchone()
    
    if cache:
        if (len(posts)) != 0:
            p.sadd(f'posts:{locality}:{epoch}', *posts)
        p.execute()
    
    return (posts, hot_factors)

def populate_posts_data(posts):
    p1 = r.pipeline()
    p2 = r.pipeline()

    # collect post data for each post
    for post in posts:
        p1.get('post:{post}')
        p2.get('post:{post}:likes')

    data = p1.execute()
    likes = p2.execute()

    # fetch post data from DB if nonexistent
    for i in range(len(posts)):
        keys = unpack(posts[i])

        if data[i] is None or likes[i] is None:
            # again, bothers me that I cannot use executemany
            # to save on RTT
            cursor.execute('SELECT creator, creationTime, title, description, address, lat, lng, likes\
                FROM Posts\
                WHERE creator=?\
                AND creationTime=?')
            row = cursor.fetchone()

            post_dict = {
                'creator': row[0],
                'creationTime': row[1],
                'title': row[2],
                'description': row[3],
                'address': row[4],
                'lat': row[5],
                'lng': row[6]
            }
            data[i] = post_dict
            p1.set(f'post:{posts[i]}', json.dumps(post_dict))
            p1.set(f'post:{posts[i]}:likes', row[7])
            # add likes
            post_dict['likes'] = row[7]
        else:
            data[i] = json.loads(data[i])
            data[i]['likes'] = likes[i]

    p1.execute()
    return data

def grow_trees(user, locality, lean ,fat):
    now = int(time.time())
    # first fetch most recent posts...
    epoch = now - now % TIME_BLOCK_SIZE
    p = pipeline()

    tail = r.get(f'user:{user}:session:tail')
    if tail is None or epoch - tail >= (TIME_BLOCK_SIZE*2):
        tail = epoch - TIME_BLOCK_SIZE
        p.set(f'user:{user}:session:tail', tail)
    
    seen = r.smembers(f'user:{user}:session:seen')
    if len(seen) >= MAX_SEEN_POSTS:
        # flush seen posts
        r.delete(f'user:{user}:session:seen')
        seen = {} 

    while lean.size() < MIN_TREE_SIZE:
        posts, hot_factors = fetch_posts(epoch, locality)

        # no more posts :(
        if len(posts) == 0:
            break

        for i in range in len(posts):
            # if post already seen by user, ignore
            if posts[i] in seen:
                continue

            post = posts[i]
            keys = unpack(post)
            
            if is_cold(keys[1], hot_factors[i]):
                fat.add(post, hot_factors[i])
            else:
                lean.add(post, hot_factors[i])
                p.sadd(f'user:{user}:session:tree', post)

            # then continue fetching posts from the past
            epoch = tail
            if lean.size() < MIN_TREE_SIZE:
                tail -= TIME_BLOCK_SIZE
        
    p.set(f'user:{user}:session:tail', tail)
    p.execute()

def build_trees(user, locality):
    # stores post ids. post ids are in the form of [creator]_[creationTime]
    lean = WTree()
    fat = WTree()

    p = r.pipeline()
    # (redis) set of post ids.
    posts = r.smembers(f'user:{user}:session:tree')
    posts_list = []
    hot_factors = []

    for post in posts:
        posts_list.append(post)
        p.get(f'post:{post}:hot_factor')

    hot_factors = p.execute()
    calculate_hot_factors_batch(posts_list, hot_factors)

    for i, post in enumerate(posts_list):
        keys = unpack(post)

        if is_cold(keys[1], hot_factors[i]):
            fat.add(post, hot_factors[i])
        else:
            lean.add(post, hot_factors[i])

    # if tree is too small...
    if lean.size() < MIN_TREE_SIZE:
        grow_trees(user, locality, lean, fat)
    
    return lean, fat

def get_feed_page(user, lean, fat, fat_percentage=FAT_PERCENT, page_size=PAGE_SIZE):
    posts = []
    p = r.pipeline()

    for i in range(page_size):
        coin = random.randint(1, 100)
        if coin <= fat_percentage:
            # sampling without replacement ensures
            # no duplicate posts per page
            post = fat.pop()
        else:
            post = lean.pop()
        
        # remove from tree
        p.srem(f'user:{user}:session:tree', post)    
        posts.append(post)

    p.execute()
    return posts

