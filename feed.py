## Creates Flask app.
##
## Defines routing and controllers for endpoints,
## starts async worker to process background tasks.

import queue
from _thread import start_new_thread
import json
import logging
import time
from flask import Flask, request, jsonify

import async_worker
from app_state import r, config
from services import build_tree, get_feed_page, populate_posts_data, fan_out

# log configuration
logging.basicConfig(filename=config['app']['LOG_FILE'],
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(threadName)s : %(message)s')

# Where async work gets queued.
#
# Async work is work that doesn't need to be done
# immediately during a client request.
work_q = queue.Queue()
start_new_thread(async_worker.run, (work_q,))

app = Flask('feed')

## Simple health check.
@app.route('/ping')
def ping():
    app.logger.info('%s %s', request.method, request.url)
    return 'PONG'

## Generates page of relevant posts
## for a given user.
@app.route('/<user>/feed')
def get_feed(user):
    app.logger.info('%s %s', request.method, request.url)
    page = r.get(f'user:{user}:session:next')

    try:
        latlng = request.args.get('latlng').split(',')
        latlng[0] = float(latlng[0])
        latlng[1] = float(latlng[1])

        token = request.args.get('session_token')
        num_posts = int(request.args.get('page_size'))
    
        # if next page cached
        if page is not None:
            work_q.put(lambda: async_worker.increment_seen(page, data_type='json_bytes'))
            work_q.put(lambda: async_worker.cache_next_page(user, latlng, session_token=token))
            return page

        lean, fat = build_tree(user, latlng, token)
        page = get_feed_page(user, lean, fat, page_size=num_posts)

        # cache next page for fast serving
        work_q.put(lambda : async_worker.increment_seen(page, data_type='list'))
        work_q.put(lambda : async_worker.cache_next_page(user, latlng, lean, fat, session_token=token))
        return jsonify(populate_posts_data(page, user))
    # can get more specific later if need be
    except Exception as e:
        app.logger.error(e)
        return 'internal server error', 500

## When a post is created, it must
## be "fanned out" to nearby users.
@app.route('/fanout')
def get_fan_out():
    app.logger.info('%s %s', request.method, request.url)
    try:
        latlng = request.args.get('latlng').split(',')
        latlng[0] = float(latlng[0])
        latlng[1] = float(latlng[1])

        postId = request.args.get('post_id')
        fan_out(latlng, postId)
        return 'OK'
    except Exception as e:
        app.logger.error(e)
        return 'internal server error', 500


