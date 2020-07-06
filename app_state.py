## Store global variables (such as config and Redis connection) here

import configparser
import redis

config = configparser.ConfigParser()
config.read('./app.ini')

r = redis.Redis(host=config['redis']['host'], port=6379, db=0)
            
