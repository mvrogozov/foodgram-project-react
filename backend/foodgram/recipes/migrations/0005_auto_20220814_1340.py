# Generated by Django 3.2.14 on 2022-08-14 13:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_ingredientforrecipe_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientforrecipe',
            name='amount',
            field=models.FloatField(max_length=10, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
        migrations.AddIndex(
            model_name='ingredient',
            index=models.Index(fields=['name'], name='recipes_ing_name_164c6a_idx'),
        ),
    ]