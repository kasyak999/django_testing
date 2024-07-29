from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.fixture
def urls(news, coment):
    """Фикстура для url"""
    return {
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup'),
        'home': reverse('news:home'),
        'detail': reverse('news:detail', args=[news.id]),
        'edit': reverse('news:edit', args=[coment.id]),
        'delete': reverse('news:delete', args=[coment.id]),
    }


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
def test_status_codes(name_url, client_, code, urls):
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
