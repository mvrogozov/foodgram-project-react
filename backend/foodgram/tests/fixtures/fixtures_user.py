import pytest


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        password='11111111'
    )


@pytest.fixture
def user_client():
    from rest_framework.test import APIClient

    client = APIClient()
    return client