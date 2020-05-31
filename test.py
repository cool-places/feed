import time
import random

from wtree import WTree
from stream import Stream
from app_state import block_size

def nearest_block(ts):
    return ts - ts % block_size

def calculate_hot_factor(post):
    age = int(time.time()) - post[1]
    return max(1, int((post[2]/post[3]) * 100) + post[2]//10 - (age//block_size) * 10)

posts = Stream('seattle')
most_recent_posts = posts.get_tip()
lean = WTree()
fat = WTree()

for post in most_recent_posts:
    age = (int(time.time()) - post[1])
    hf = calculate_hot_factor(post)
    # print(f'{post[0]}, {age}h, likes: {post[2]}, hf: {hf}') 

    # 10 is an arbitrary number...
    if age > block_size and hf < 10:
        fat.add((post[0], post[1], post[2], post[3]), hf)
    else:
        lean.add((post[0], post[1], post[2], post[3]), hf)

cur = posts.tip - block_size
while lean.size() != 0 or fat.size() != 0:
    user_in = input('Press enter to receive next page!')

    if (lean.size() == 0):
        num_fat = 25
    else:
        num_fat = random.randint(0, 5)
        
    num_lean = 25 - num_fat

    page = lean.pop_multi(num_lean) + fat.pop_multi(num_fat)
    for post in page:
        # print(post)
        age = (time.time() - post[1]) // 3600
        hf = calculate_hot_factor(post)
        print(f'  {age}h  likes: {post[2]}  hf: {hf}')

    while (cur >= 0 and lean.size() < 100):
        block = posts.get_block(cur)

        for post in block:
            age = int(time.time()) - post[1]
            hf = calculate_hot_factor(post)

            # 10 is an arbitrary number...
            if age > block_size and hf < 10:
                fat.add((post[0], post[1], post[2], post[3]), hf)
            else:
                lean.add((post[0], post[1], post[2], post[3]), hf)

        cur -= block_size
    

print('ran out of posts :(')




