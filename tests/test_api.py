import requests

r = requests.get('http://localhost:5000/ping')
print(r.text)

r = requests.get('http://localhost:5000/youn/seattle/feed')
print(r.json())

