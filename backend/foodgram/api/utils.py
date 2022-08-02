import requests
from rest_framework import serializers
import json


def fill_db(path_to_file):
    url = 'http://127.0.0.1:8000/api/ingredients/'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    path_to_file = '../../../data/ingredients.json'
    with open(path_to_file) as f:
        data = json.load(f)
    for item in data:
        r = requests.post(
            url,
            json=item,
            headers=headers)
        print(item, '\n')


def is_me(value):
    if value == 'me':
        raise serializers.ValidationError(
            'Нельзя использовать зарезервированное имя "me"'
        )
    return value
