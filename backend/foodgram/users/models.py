from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, Q


class User(AbstractUser):

    login = models.CharField(
        'login',
        max_length=150,
        unique=True,
        db_index=True
    )
    name = models.CharField(
        'name',
        max_length=150,
        unique=False
    )
    surname = models.CharField(
        'surname',
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
