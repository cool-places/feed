import redis
r = redis.Redis(host='10.0.0.8', port=6379, db=0)
val = r.get('test')
print(val)
