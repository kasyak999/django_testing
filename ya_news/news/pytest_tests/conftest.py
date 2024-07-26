# conftest.py
import pytest

# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment
from datetime import datetime
from django.conf import settings
from datetime import datetime, timedelta 


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):  
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def unauthorized_client():
    """Не авторизированый"""
    return Client()


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    return News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )


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

    # for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
    #         news = News(title=f'Новость {index}', text='Просто текст.')
    #         all_news.append(news)
    #     News.objects.bulk_create(all_news) 


@pytest.fixture
def coment(news, author):
    coment = Comment.objects.create(  # Создаём объект заметки.
        news=news,
        text='Текст заметки',
        author=author,
    )
    return coment


@pytest.fixture
def form_data():
    return {'text': 'Текст заметки новый'}
