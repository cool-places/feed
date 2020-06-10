## Contains policy relating to feed generation
## for a user.

import time

TIME_BLOCK_SIZE = 5 * 3600 * 1000 # 5 hours
MAX_SEEN_POSTS = 10000
MIN_TREE_SIZE = 50
PAGE_SIZE = 5
FAT_PERCENT = 10
HOT_FACTOR_EXPIRATION = 120 # 120 secs
# When this app was born. No posts
# exist before this time
INCEPTION = 1588550400 * 1000
# 1 is 0.0001 deg. So this represents 0.25 deg (for lat, lng)
GRID_SIZE = 2500
# fetch posts within 30 miles of user
FETCH_RADIUS = 48280 # ~30 miles

# used as relative weights when sampling posts
def calculate_hot_factor(creationTime, likes, seen_by):
    age = int(time.time() * 1000) - creationTime
    return max(1, int((likes/seen_by) * 100) + likes//10 - (age//TIME_BLOCK_SIZE) * 10)

# cold posts become part of the fat
# (gets evicted from lean tree).
def is_cold(creationTime, hot_factor):
    age = int(time.time() * 1000) - creationTime
    
    # 10 is an arbitrary number, not thought out in any way
    return age > TIME_BLOCK_SIZE and hot_factor < 10


