## Service layer. Decouples application logic from HTTP context.
##
## Majority of the logic involves fetching things from DB and caching the
## results.

import time
import random
import json
import logging

from wtree import WTree
from app_state import cursor, cnxn, r
from policy import TIME_BLOCK_SIZE, MAX_SEEN_POSTS, MIN_TREE_SIZE, \
PAGE_SIZE, FAT_PERCENT, HOT_FACTOR_EXPIRATION, \
INCEPTION, GRID_SIZE, FETCH_RADIUS, \
calculate_hot_factor, is_cold

fetch_query = '''
DECLARE @p geography = geography::Point(?, ?, 4326);
SELECT creator, creationTime, location.Lat, location.Long, votes, "views", "type"
FROM Posts WHERE location.STDistance(@p) <= ?
AND creationTime BETWEEN ? and ?;
'''

## Break down a post id into its composite key components.
def post_id_to_list(id):
    keys = id.split('_')
    keys[1] = int(keys[1])
    return keys

## Serializes a location loc: list[float], where
## index 0 is lat and index 1 is lng.
##
## Used as keys to cache DB query results in redis.
def location_to_str(loc):
    return str(loc[0]) + ',' + str(loc[1]) 

## Snaps location to the nearest grid point.
## 
## Grid is comprised of GRID_SIZE x GRID_SIZE squares.
def snap_to_grid(loc):
    lat = int(loc[0]*10000)
    r = lat % GRID_SIZE
    lat -= r
    if (r >= GRID_SIZE // 2):
        lat += GRID_SIZE
    loc[0] = lat / 10000.0

    lng = int(loc[1]*10000)
    r = lng % GRID_SIZE
    lng -= r
    if (r >= GRID_SIZE // 2):
        lng += GRID_SIZE
    loc[1] = lng / 10000.0

## Fans out a post at location loc to nearby grid
## points.
def fan_out(loc, post):
    now = int(time.time() * 1000)
    epoch = now - now % TIME_BLOCK_SIZE
    p = r.pipeline()    
    snap_to_grid(loc)

    boundaries = []
    N, E, S, W = range(4)
    boundaries.append(loc[0] + 1) # North
    boundaries.append(loc[1] + 1) # East
    boundaries.append(loc[0] - 1) # South
    boundaries.append(loc[1] - 1) # West

    points = []
    lng = boundaries[E]
    # from East -> West
    while lng != boundaries[W]:
        lat = boundaries[S]
        # from South -> North
        while lat != boundaries[N]:
            loc_str = location_to_str([lat, lng])
            p.exists(f'posts:{loc_str}:{epoch}')
            points.append(loc_str)

            lat += (GRID_SIZE / 10000)
        lng -= (GRID_SIZE / 10000)

    results = p.execute()
    for i in range(len(results)):
        if results[i]:
            p.sadd(f'posts:{points[i]}:{epoch}', post)
    
    p.execute()
    return points

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
            p.get(f'post:{post}:votes')
            p.get(f'post:{post}:views')

    stats = p.execute()
    inputs = []
    for i in range(0, len(stats), 2):
        post = posts[indices[i//2]]
        keys = post_id_to_list(post)

        # if votes or views doesn't exist
        if stats[i] is None or stats[i+1] is None:
            # kinda bothers me to have to go back and forth to DB
            # for every post...but hopefully there aren't that
            # many posts whose stats are not cached
            cursor.execute('SELECT votes, "views" FROM Posts\
                    WHERE creator=? AND creationTime=?', keys[0], keys[1])
            row = cursor.fetchone()
            stats[i], stats[i+1] = row[0], row[1]
            p.set(f'post:{post}:votes', row[0])
            p.set(f'post:{post}:views', row[1])
        else:
            stats[i], stats[i+1] = int(stats[i]), int(stats[i+1])

        hf = calculate_hot_factor(keys[1], stats[i], stats[i+1])
        hot_factors[indices[i//2]] = hf

        p.set(f'post:{post}:hot_factor', hf)
        # force app to recalculate hot factor
        p.expire(f'post:{post}:hot_factor', HOT_FACTOR_EXPIRATION)

    p.execute()

## Fetch all posts in epoch at location.
##
## If cache is True, caches data fetched
## from DB.
def fetch_posts(epoch, loc, cache=True):
    logging.info(f'fetching posts in [{epoch}, {epoch + TIME_BLOCK_SIZE - 1}]');

    snap_to_grid(loc)
    loc_str = location_to_str(loc)

    p = r.pipeline()
    posts = r.smembers(f'posts:{loc_str}:{epoch}')
    hot_factors = []

    if len(posts) != 0:
        # posts is a set in redis cache. This is
        # to (naively) support concurrent caching of posts
        # without worrying about duplicate posts
        posts = list(posts)
        for i in range(len(posts)):
            posts[i] = posts[i].decode('utf-8')
            p.get(f'post:{posts[i]}:hot_factor')

        hot_factors = [None if elem is None else int(elem) for elem in p.execute()]
        calculate_hot_factors_batch(posts, hot_factors)
        return posts, hot_factors

    posts = []
    cursor.execute(fetch_query, loc[0], loc[1], FETCH_RADIUS, epoch, epoch + TIME_BLOCK_SIZE - 1)
    
    row = cursor.fetchone()
    while row:
        post_id = f'{row[0]}_{row[1]}'
        posts.append(post_id)

        hf = calculate_hot_factor(row[1], row[4], row[5])
        hot_factors.append(hf)

        if cache:
            p.set(f'post:{post_id}:votes', row[4])
            p.set(f'post:{post_id}:views', row[5])
            p.set(f'post:{post_id}:hot_factor', hf)
            # force app to recalculate hot factor
            p.expire(f'post:{post_id}:hot_factor', HOT_FACTOR_EXPIRATION)

        row = cursor.fetchone()
    
    if cache:
        if (len(posts)) != 0:
            p.sadd(f'posts:{loc_str}:{epoch}', *posts)
        p.execute()
    
    return posts, hot_factors

## Given a list of post IDs, return a list
## with the posts' data.
def populate_posts_data(posts, user):
    if (len(posts) == 0):
        return []

    # first get set of all posts user voted on
    if (not r.exists(f'user:{user}:voted:up')):
        p = r.pipeline()
        cursor.execute('SELECT postCreator, postCreationTime FROM Votes WHERE voter=? AND dir=?', user, 'UP')
        voted = cursor.fetchall()

        for (post_creator, post_creation_time) in voted:
            p.sadd(f'user:{user}:voted:up', f'{post_creator}_{post_creation_time}')

        p.execute()
    
    p1 = r.pipeline()
    p2 = r.pipeline()
    p3 = r.pipeline()

    # collect post data, vote count, and user-vote data for each post
    for post in posts:
        p1.get(f'post:{post}')
        p2.get(f'post:{post}:votes')
        p3.sismember(f'user:{user}:voted:up', post)

    data = p1.execute()
    votes = p2.execute()
    voted = p3.execute()

    # fetch post data from DB if not cached
    for i in range(len(posts)):
        creator, creation_time = post_id_to_list(posts[i])

        if data[i] is None or votes[i] is None:
            # cannot use executemany for SELECT statements
            # to save on RTT
            cursor.execute('SELECT creator, creationTime, location.Lat, location.Long, title, "type", votes\
                FROM Posts\
                WHERE creator=?\
                AND creationTime=?', creator, creation_time)
            row = cursor.fetchone()

            post_dict = {
                'creator': row[0],
                'creationTime': row[1],
                'lat': row[2],
                'lng': row[3],
                'title': row[4],
                'type': row[5]
            }
            data[i] = post_dict
            p1.set(f'post:{posts[i]}', json.dumps(post_dict))
            p1.set(f'post:{posts[i]}:votes', row[6])
            # add votes data
            post_dict['votes'] = row[6]
            post_dict['voted'] = 'UP' if voted[i] else 'NONE'
        else:
            data[i] = json.loads(data[i])
            data[i]['votes'] = int(votes[i])
            data[i]['voted'] = 'UP' if voted[i] else 'NONE'

    p1.execute()
    return data

## Grow passed in tree, gradually fetching older
## posts.
##
## If new session token is given, it resets the session tail,
## which represents the next older epoch to fetch posts from.
def grow_tree(user, loc, lean, fat, session_token):
    snap_to_grid(loc)
    loc_str = location_to_str(loc)

    now = int(time.time() * 1000)
    # first fetch most recent posts (in current epoch)
    epoch = now - now % TIME_BLOCK_SIZE
    p = r.pipeline()

    # determine whether this is a new feed session.
    last_token = r.get(f'user:{user}:session')
    if last_token is None:
        p.set(f'user:{user}:session', session_token)
        tail = epoch - TIME_BLOCK_SIZE
    elif last_token.decode('utf-8') != session_token:
        tail = epoch - TIME_BLOCK_SIZE
        r.delete(f'user:{user}:session:seen')
        p.set(f'user:{user}:session', session_token)
    else:
        tail = r.get(f'user:{user}:session:tail')
        if tail is None:
            tail = epoch - TIME_BLOCK_SIZE
        else:
            tail = int(tail)
    
    seen = r.smembers(f'user:{user}:session:seen')
    if len(seen) >= MAX_SEEN_POSTS:
        # flush seen posts
        r.delete(f'user:{user}:session:seen')
        seen = set()
    
    while lean.size() < MIN_TREE_SIZE and epoch >= INCEPTION:
        posts, hot_factors = fetch_posts(epoch, loc)

        for i in range(len(posts)):
            # if post already seen by user, ignore
            if bytes(posts[i], 'utf-8') in seen:
                continue

            post = posts[i]
            keys = post_id_to_list(post)
            
            if is_cold(keys[1], hot_factors[i]):
                fat.add(post, hot_factors[i])
            else:
                lean.add(post, hot_factors[i])
                p.sadd(f'user:{user}:session:tree', post)

        # continue fetching older pasts
        epoch = tail
        if lean.size() < MIN_TREE_SIZE and epoch >= INCEPTION:
            tail -= TIME_BLOCK_SIZE
        
    p.set(f'user:{user}:session:tail', tail)
    p.execute()

## Build & cache tree for user.
def build_tree(user, loc, session_token):
    snap_to_grid(loc)
    loc_str = location_to_str(loc)
    # trees store post ids.
    # post ids are in the form of [creator]_[creationTime]
    lean = WTree()
    fat = WTree()

    p = r.pipeline()
    posts = r.smembers(f'user:{user}:session:tree')
    posts_list = []
    hot_factors = []

    for post in posts:
        posts_list.append(post.decode('utf-8'))
        p.get(f'post:{post}:hot_factor')

    hot_factors = p.execute()
    calculate_hot_factors_batch(posts_list, hot_factors)

    # trim tree
    for i, post in enumerate(posts_list):
        keys = post_id_to_list(post)

        if is_cold(keys[1], hot_factors[i]):
            fat.add(post, hot_factors[i])
        else:
            lean.add(post, hot_factors[i])

    # if tree is too small...
    if lean.size() < MIN_TREE_SIZE:
        grow_tree(user, loc, lean, fat, session_token)
    
    return lean, fat

## Given lean and fat trees, generate a page
## by sampling from them.
def get_feed_page(user, lean, fat, fat_percentage=FAT_PERCENT, page_size=PAGE_SIZE):
    posts = []
    p = r.pipeline()

    for i in range(page_size):
        coin = random.randint(1, 100)
        if coin <= fat_percentage and fat.size() > 0:
            # sampling without replacement ensures
            # no duplicate posts per page
            post = fat.pop()
        elif lean.size() > 0:
            post = lean.pop()
        elif fat.size() > 0:
            post = fat.pop()
        else:
            break
        
        # remove from tree
        p.srem(f'user:{user}:session:tree', post)    
        posts.append(post)

    if len(posts) > 0:
        p.sadd(f'user:{user}:session:seen', *posts)
        p.execute()

    return posts

