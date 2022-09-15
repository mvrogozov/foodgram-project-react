import pytest
from rest_framework.test import APIClient


@pytest.fixture
def project_user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        password='11111111'
    )


@pytest.fixture
def project_user_client():
    client = APIClient()
    client.force_authenticate(project_user)
    return client


@pytest.fixture
def project_admin(django_user_model):
    return django_user_model.objects.create_user(
        username='TestAdmin',
        password='22222222',
        is_staff=True
    )


@pytest.fixture
def project_admin_client():
    client = APIClient()
    client.force_authenticate(project_admin)
    return client

@pytest.fixture
def anonymous_client():
    client = APIClient()
    return client
