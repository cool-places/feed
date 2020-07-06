## Contains various policy relating to feed generation.

import time

TIME_BLOCK_SIZE = 24 * 3600 * 1000 # 24 hours
MAX_SEEN_POSTS = 10000
MIN_TREE_SIZE = 50
PAGE_SIZE = 5
FAT_PERCENT = 5
HOT_FACTOR_EXPIRATION = 120 # 120 secs
# When this app was first born. By definition, no posts
# exist before this time
INCEPTION = 1588550400 * 1000

## Measure of how "hot" a post is.
## It is a function of its age, votes, and views (how many people have seen it).
##
## It is used as relative weights to randomly sample posts
## for a user's feed.
def calculate_hot_factor(creationTime, votes, views):
    age = int(time.time() * 1000) - creationTime
    return max(1, int((votes/views) * 100) + votes//10 - (age//TIME_BLOCK_SIZE) * 10)

## Determines whether a post is "cold" or not.
##
## Cold posts move from lean to fat tree.
def is_cold(creationTime, hot_factor):
    age = int(time.time() * 1000) - creationTime
    
    # 10 is an arbitrary number, not thought out in any way
    return age > TIME_BLOCK_SIZE and hot_factor < 10
