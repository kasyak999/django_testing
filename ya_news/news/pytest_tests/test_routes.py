from http import HTTPStatus
from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news')),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Проверим, что анонимному пользователю доступно"""
    url = reverse(name, args=[args.id] if args is not None else args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, expected_status, coment
):
    """Страницы удаления и редактирования комментария доступны автору"""
    url = reverse(name, args=[coment.id])
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',),
)
def test_anonim(name, coment, client):
    """Страницы удаления и редактирования для анонима"""
    url = reverse(name, args=[coment.id])
    response = client.get(url)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
