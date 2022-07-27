import pytest

from rest_framework.test import APIClient
from recipes.models import Tag
#from recipes.models import Tag


'''class TestTagApi:

    @pytest.mark.django_db(transaction=True)
    def test_tags_not_found(self, user_client, tag):
        response = user_client.get(f'/api/tags/')

        assert response.status_code != 404, (
            'Страница `/api/tags/` не найдена'
        )'''


#settings.configure()

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        password='11111111'
    )


@pytest.fixture
def user_client():
    client = APIClient()
    return client


@pytest.fixture
def tag():
    
    return Tag.objects.create(
        tag_name='имя тега 1',
        color='dadada',
        slug='tagslug1'
    )

@pytest.fixture
def tag_2():
    
    return Tag.objects.create(
        tag_name='имя тега 2',
        color='232323',
        slug='tagslug2'
    )


@pytest.mark.django_db(transaction=True)
def test_tags_not_found(user_client, tag):
        response = user_client.get(f'/api/tags/')

        assert response.status_code != 404, (
            'Страница `/api/tags/` не найдена'
        )