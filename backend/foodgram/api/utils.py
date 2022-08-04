import requests
from rest_framework import serializers
from django.core.files.base import ContentFile
import json
import base64


def serializer_decode_image(data):
    try:
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    except ValueError:
        raise serializers.ValidationError('wrong image')
    return data


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
