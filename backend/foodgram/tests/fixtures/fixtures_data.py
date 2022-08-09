import tempfile

import pytest


@pytest.fixture
def tag():
    from recipes.models import Tag
    return Tag.objects.create(
        tag_name='имя тега 1',
        color='dadada',
        slug='tagslug1'
    )

@pytest.fixture
def tag_2():
    from recipes.models import Tag
    return Tag.objects.create(
        tag_name='имя тега 2',
        color='232323',
        slug='tagslug2'
    )