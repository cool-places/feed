from pymemcache.client.base import Client

client = Client(('10.0.0.8', 11211))
client.set('hello', 'world!')
result = client.get('hello')
print(result)
