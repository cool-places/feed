## Entry point of feed generation service.
##
## Defines routing and controllers for endpoints.
## Starts async worker to process background tasks.

import queue
from _thread import start_new_thread
import json
from flask import Flask, request, jsonify

import async_worker
from app_state import r
from services import build_trees, get_feed_page, populate_posts_data

# Where async work will be queued up.
#
# Async work is work that doesn't need to be done
# immediately during a client request.
work_q = queue.Queue()
start_new_thread(async_worker.run, (work_q,))

app = Flask(__name__)

# health check
@app.route('/ping')
def ping():
    return 'PONG'

@app.route('/<user>/<locality>/feed')
def get_feed(user, locality):
    page = r.get(f'user:{user}:session:next')
    
    if page is not None:
        work_q.put(lambda: async_worker.increment_seen(page, unmarshal=True))
        work_q.put(lambda: async_worker.cache_next_page(user, locality))
        return page

    lean, fat = build_trees(user, locality)
    page = get_feed_page(user, lean, fat)

    # save next page to cache for fast serving
    work_q.put(lambda : async_worker.increment_seen(page, unmarshal=False))
    work_q.put(lambda : async_worker.cache_next_page(user, locality, lean, fat))
    return jsonify(populate_posts_data(page))


