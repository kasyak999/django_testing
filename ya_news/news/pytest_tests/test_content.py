import pytest
from news.forms import CommentForm
from django.conf import settings
from django.urls import reverse


@pytest.fixture
def urls(news):
    """Фикстура для url"""
    return {
        'home': reverse('news:home'),
        'detail': reverse('news:detail', args=[news.id]),
    }


@pytest.mark.django_db
def test_news_on_the_main_page(client, news_all, urls):
    """Количество новостей на главной странице"""
    response = client.get(urls['home'])
    assert len(
        response.context['object_list']
    ) <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_sorting_the_news(client, news_all, urls):
    """Новости отсортированы от самой свежей к самой старой"""
    response = client.get(urls['home'])
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_sorting_the_comment(client, coment_all, urls):
    """Комментарии отсортированы от самой свежей к самой старой"""
    response = client.get(urls['detail'])
    object_list = response.context['news'].comment_set.all()
    all_dates = [coment.created for coment in object_list]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_pages_contains_form(author_client, urls):
    """форма для отправки комментария для авторизированого"""
    response = author_client.get(urls['detail'])
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_form_for_anonymous(client, urls):
    """форма для отправки комментария для анонимного"""
    response = client.get(urls['detail'])
    assert 'form' not in response.context
