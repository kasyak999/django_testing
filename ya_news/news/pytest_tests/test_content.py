from django.urls import reverse
import pytest
from news.forms import CommentForm
from django.conf import settings


@pytest.mark.django_db
def test_news_on_the_main_page(client, news_all):
    """Количество новостей на главной странице"""
    url = reverse('news:home')
    response = client.get(url)
    assert len(
        response.context['object_list']
    ) <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sorting_the_news(client, news_all):
    """Новости отсортированы от самой свежей к самой старой"""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, note_in_list',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('unauthorized_client'), True),
    )
)
def test_notes_list_for_different_users(
        news, parametrized_client, note_in_list
):
    url = reverse('news:home')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (news in object_list) is note_in_list


@pytest.mark.django_db
def test_pages_contains_form(author_client, news):
    """форма для отправки комментария для авторизированого"""
    url = reverse('news:detail', args=[news.id])
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_form_for_anonymous(client, news):
    """форма для отправки комментария для анонимного"""
    url = reverse('news:detail', args=[news.id])
    response = client.get(url)
    assert 'form' not in response.context
