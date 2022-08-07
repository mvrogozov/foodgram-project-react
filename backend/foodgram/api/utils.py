import requests
from rest_framework import serializers
from django.core.files.base import ContentFile
import json
import base64
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import mm, inch
import io
import os
from reportlab.pdfbase import pdfmetrics
from django.conf import settings

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


def create_pdf(shopping_list):
    FONT_SIZE = 12
    A4_WIDTH = 210 * mm
    A4_HEIGHT = 297 * mm
    buffer = io.BytesIO()
    pdf_object = canvas.Canvas(buffer, pagesize='A4')
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(settings.TEMPLATES_DIR, 'arial.ttf'), 'UTF-8'))
    pdf_object.setFillColorRGB(0.2, 0.2, 0.9)
    x = 20
    y = A4_HEIGHT - 150
    pdf_object.setFont('Arial', FONT_SIZE + 4)
    pdf_object.drawString(x + 200, y + 50, 'Список покупок.')
    pdf_object.setFont('Arial', FONT_SIZE)
    for item, amount in shopping_list.items():
        pdf_object.drawString(x, y, f'{item}: {str(amount[0])} {amount[1]}')
        y -= 20
        if y < 30:
            pdf_object.showPage()
            pdf_object._pageNumber += 1
            pdf_object.setFont('Arial', FONT_SIZE)
            pdf_object.setFillColorRGB(0.2, 0.2, 0.7)
            y = A4_HEIGHT - 10
    pdf_object.drawString(x, y, '_________________________________________')
    pdf_object.showPage()
    pdf_object.save()
    buffer.seek(0)
    return buffer
