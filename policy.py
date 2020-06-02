## Contains policy relating to feed generation
## for a user.

import time

TIME_BLOCK_SIZE = 24 * 3600 # 24 hours
MAX_SEEN_POSTS = 10000
MIN_TREE_SIZE = 100
PAGE_SIZE = 25
FAT_PERCENT = 10

# used as relative weights when sampling posts
def calculate_hot_factor(creationTime, likes, seen_by):
    age = int(time.time()) - creationTime
    return max(1, int((likes/seen_by) * 100) + likes//10 - (age//TIME_BLOCK_SIZE) * 10)

# cold posts become part of the fat
# (gets evicted from lean tree).
def is_cold(creationTime, hot_factor):
    age = int(time.time()) - creationTime
    
    # 10 is an arbitrary number, not thought out in any way
    if age > TIME_BLOCK_SIZE and hot_factor < 10:

