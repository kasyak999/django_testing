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
    'name_url, client_, code',
    (
        (
            'edit', pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            'edit', pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            'delete', pytest.lazy_fixture('not_author_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            'delete', pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
    )
)
def test_pages_availability_for_different_users_11(
        name_url, client_, code, urls
):
    """Страницы удаления и редактирования комментария доступны автору"""
    assert client_.get(urls[name_url]).status_code == code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name_url, expected_url',
    (
        ('edit', 'login'),
        ('delete', 'login'),
    ),
)
def test_anonim(name_url, expected_url, client, urls):
    """Страницы удаления и редактирования для анонима"""
    response = client.get(urls[name_url])
    expected_url = f'{urls[expected_url]}?next={urls[name_url]}'
    assertRedirects(response, expected_url)
