# Generated by Django 3.2.14 on 2022-07-27 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0009_auto_20220727_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(help_text='Избранное', on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.recipe', verbose_name='Избранное'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(help_text='Избранное для', on_delete=django.db.models.deletion.CASCADE, related_name='favorite_for', to=settings.AUTH_USER_MODEL, verbose_name='Избранное для'),
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipes', models.ManyToManyField(help_text='Список покупок', related_name='shopping_list', to='recipes.Recipe', verbose_name='Список покупок')),
                ('user', models.ForeignKey(help_text='Список покупок', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_list', to=settings.AUTH_USER_MODEL, verbose_name='Список покупок')),
            ],
        ),
    ]
