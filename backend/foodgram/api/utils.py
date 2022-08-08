from rest_framework import serializers
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import mm
import io
import os
from reportlab.pdfbase import pdfmetrics
from django.conf import settings


def is_me(value):
    if value == 'me':
        raise serializers.ValidationError(
            'Нельзя использовать зарезервированное имя "me"'
        )
    return value


def create_pdf(shopping_list):
    FONT_SIZE = 12
    A4_HEIGHT = 297 * mm
    buffer = io.BytesIO()
    pdf_object = canvas.Canvas(buffer, pagesize='A4')
    pdfmetrics.registerFont(
        TTFont(
            'Arial',
            os.path.join(settings.TEMPLATES_DIR, 'arial.ttf'), 'UTF-8'
        )
    )
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
