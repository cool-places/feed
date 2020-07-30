## Store global variables (such as config and Redis connection) here

import configparser

config = configparser.ConfigParser()
config.read('./app.ini')

            
