import pytest
from rest_framework.test import APIClient

from recipes.models import Tag


@pytest.mark.django_db(transaction=True)
def test_endpoints_not_found(project_user_client, tag):
    response = project_user_client.get(f'/api/tags/')
    assert response.status_code != 404, (
        'Страница `/api/tags/` не найдена'
    )

    response = project_user_client.get(f'/api/ingredients/')
    assert response.status_code != 404, (
        'Страница `/api/ingredients/` не найдена'
    )

    response = project_user_client.get(f'/api/recipes/')
    assert response.status_code != 404, (
        'Страница `/api/recipes/` не найдена'
    )

    response = project_user_client.get(f'/api/users/')
    assert response.status_code != 404, (
        'Страница `/api/users/` не найдена'
    )

    response = project_user_client.get(f'/api/tags/')
    assert response.status_code != 404, (
        'Страница `/api/tags/` не найдена'
    )

    

@pytest.mark.django_db(transaction=True)
def test_endpoint_access(
    project_admin_client,
    project_user_client,
    project_user,
    anonymous_client
):
    data = {}
    endpoint = '/api/users/'
    response = project_admin_client.post(endpoint, data=data)
    assert response.status_code == 400, (
        f'Неверный ответ при POST запросе с неправильными данными к {endpoint}'
    )

    endpoint = '/api/users/'
    response = anonymous_client.post(endpoint, data=data)
    assert response.status_code == 400, (
        f'''
        Неверный ответ при POST запросе с неправильными данными к {endpoint}
        '''
    )

    endpoint = f'/api/users/{project_user.id}/subscribe/'
    response = anonymous_client.post(endpoint, data=data)
    assert response.status_code == 401, (
        f'''
        Неверный ответ при неавторизаванном GET запросе к {endpoint}
        '''
    )

    endpoint = '/api/users/me/'
    response = anonymous_client.get(endpoint, data=data)
    assert response.status_code == 401, (
        f'''
        Неверный ответ при неавторизаванном GET запросе к {endpoint}
        '''
    )

    
