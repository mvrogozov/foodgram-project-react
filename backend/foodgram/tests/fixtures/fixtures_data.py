import tempfile
import pytest

from recipes.models import Tag


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