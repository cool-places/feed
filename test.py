import time
import random

# from wtree import WTree
from stream import Stream
from app_state import block_size

def nearest_block(ts):
    return ts - ts % block_size

def calculate_hot_factor(post):
    age = int(time.time()) - post[1]
    return max(1, int((post[2]/post[3]) * 100) + post[2]//10 - (age//block_size) * 10)

posts = Stream('seattle')
most_recent_posts = posts.get_tip()
# lean = WTree()
# # 2nc chance for posts
# fat = WTree()

for post in most_recent_posts:
    age = (int(time.time()) - post[1]) // 3600 
    hf = calculate_hot_factor(post)
    print(f'{post[0]}, {age}h, likes: {post[2]}, hf: {hf}') 

    # # 10 is an arbitrary number...
    # if age > block_size and hf < 10:
    #     fat.add(post, hf)
    # else:
    #     lean.add(post, hf)

# cur = posts.tip - block_size
# while (cur >= 0 and lean.size() < 100):
#     block = posts.get_block(cur)

#     for post in block:
#         age = int(time.time()) - post[1]
#         hf = calculate_hot_factor(post)
#         # 10 is an arbitrary number...
#         if age > block_size and hf < 10:
#             fat.add(post, hf)
#         else:
#             lean.add(post, hf)

#     cur -= block_size

# while True:
#     user_in = input('Press enter to receive next page!')

#     num_fat = random.randint(0, 5)
#     num_lean = 25 - how_much_fat

#     page = lean.pop_multi(num_lean) + fat.pop_multi(num_fat)
#     for post in page:
#         age = (time.time() - post[1]) / 3600
#         print(f'{post[0]} {age}h likes: {post[2]}') 




