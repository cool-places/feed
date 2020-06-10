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
from services import build_trees, get_feed_page, populate_posts_data, fan_out

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

@app.route('/<user>/feed')
def get_feed(user):
    page = r.get(f'user:{user}:session:next')

    latlng = request.args.get('latlng').split(',')
    latlng[0] = float(latlng[0])
    latlng[1] = float(latlng[1])
    
    if page is not None:
        work_q.put(lambda: async_worker.increment_seen(page, unmarshal=True))
        work_q.put(lambda: async_worker.cache_next_page(user, latlng))
        return page

    lean, fat = build_trees(user, latlng)
    page = get_feed_page(user, lean, fat)

    # save next page to cache for fast serving
    work_q.put(lambda : async_worker.increment_seen(page, unmarshal=False))
    work_q.put(lambda : async_worker.cache_next_page(user, latlng, lean, fat))
    return jsonify(populate_posts_data(page))

@app.route('/fanout')
def get_fan_out():
    latlng = request.args.get('latlng').split(',')
    latlng[0] = float(latlng[0])
    latlng[1] = float(latlng[1])

    postId = request.args.get('post_id')
    fan_out(latlng, postId)
    return 'OK'


