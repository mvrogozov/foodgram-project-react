import requests
import json

url = 'http://127.0.0.1:8000/api/ingredients/'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
with open('../../../data/ingredients.json') as f:
    data = json.load(f)
for item in data:
    r = requests.post(
        url,
        json=item,
        headers=headers)
    print(item, '\n')
