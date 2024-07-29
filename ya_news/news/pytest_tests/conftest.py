import pytest
from django.test.client import Client
from news.models import News, Comment
from datetime import datetime
from django.conf import settings
from datetime import datetime, timedelta
from django.urls import reverse


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок', text='Текст заметки',
    )


@pytest.fixture
def coment(news, author):
    return Comment.objects.create(
        news=news,
        text='Текст заметки',
        author=author,
    )


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


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news_all():
    all_news = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Заголовок {i}',
            text=f'Текст заметки {i}',
            date=datetime.today() + timedelta(days=1)
        )
        all_news.append(news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def coment_all(news, author):
    all_coment = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        coment = Comment(
            news=news,
            text=f'Текст комента {i}',
            created=datetime.today() + timedelta(days=1),
            author=author,
        )
        all_coment.append(coment)
    return Comment.objects.bulk_create(all_coment)


@pytest.fixture
def form_data():
    return {'text': 'Текст заметки новый'}
