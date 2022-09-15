from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        db_index=True
    )
    first_name = models.CharField(
        'first_name',
        max_length=150,
        unique=False
    )
    last_name = models.CharField(
        'last_name',
        max_length=150,
        unique=False
    )
    email = models.EmailField(
        'email',
        max_length=254,
        unique=True
    )
    password = models.CharField(
        'password',
        max_length=150
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('username',)
