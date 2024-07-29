from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
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
        (
            'home', pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            'login', pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            'logout', pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            'signup', pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            'detail', pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
    )
)
def test_status_codes(
        name_url, client_, code, urls
):
    """Проверка статуса страниц"""
    assert client_.get(urls[name_url]).status_code == code


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name_url, expected_url',
    (
        ('edit', 'login'),
        ('delete', 'login'),
    ),
)
def test_anonymous_redirects(name_url, expected_url, client, urls):
    """Страницы удаления и редактирования для анонима"""
    response = client.get(urls[name_url])
    expected_url = f'{urls[expected_url]}?next={urls[name_url]}'
    assertRedirects(response, expected_url)
