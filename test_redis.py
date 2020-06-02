import redis
r = redis.Redis(host='10.0.0.8', port=6379, db=0)
p = r.pipeline()

p.get('test')
p.get('test2')
p.set('test2', 'Doh!')
p.sadd('test3', *[1, 2, 3])
p.expire('test2', 60)
results = p.execute()
print(results)

s1 = r.smembers('test3')
print(type(s1))
