## Creates Flask app.
##
## Defines routing and controllers for endpoints,
## starts async worker to process background tasks.

import json
import logging
import traceback
import time
from flask import Flask, request, jsonify

from app_state import config
from services import build_tree, get_feed_page

# log configuration
logging.basicConfig(filename=config['app']['LOG_FILE'],
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(threadName)s : %(message)s')

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
    try:
        app.logger.info('%s %s', request.method, request.url)
        # page = r.get(f'user:{user}:session:next')
        town = request.args.get('town')
        refresh = request.args.get('refresh') == 'true'
        num_posts = int(request.args.get('page_size'))

        user = int(user)

        lean, fat = build_tree(user, town, refresh)
        return jsonify(get_feed_page(user, lean, fat, page_size=num_posts))
    # can get more specific later if need be
    except Exception as e:
        tb = traceback.format_exc()

        print(e)
        print(tb)
        
        app.logger.error(e)
        app.logger.error(tb)
        return 'internal server error', 500

# for debugging purposes
if (__name__ == '__main__'):
    app.run('0.0.0.0', 7191)


