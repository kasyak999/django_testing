from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from news.models import News, Comment
import pytest
# Импортируем из модуля forms сообщение об ошибке:
from news.forms import WARNING, BAD_WORDS
# Дополнительно импортируем функцию slugify.
from http import HTTPStatus


# Указываем фикстуру form_data в параметрах теста.
def test_user_can_create_news_coment(author_client, news, author, form_data):
    url = reverse('news:detail', args=[news.id])
    response = author_client.post(url, data=form_data)
    assertRedirects(
        response,
        reverse('news:detail', args=[news.id]) + '#comments'
    )
    assert Comment.objects.count() == 1
    new_note = Comment.objects.get()
    assert new_note.text == form_data['text']
    assert new_note.news == news
    assert new_note.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data, news):
    url = reverse('news:detail', args=[news.id])
    # Через анонимный клиент пытаемся создать заметку:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name', BAD_WORDS
)
def test_not_unique_slug(author_client, news, name):
    url = reverse('news:detail', args=[news.id])
    response = author_client.post(url, data={'text': name})
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


# Тестирование редактирования
def test_author_can_edit_note(author_client, form_data, coment, news):
    url = reverse('news:edit', args=[coment.id])
    response = author_client.post(url, form_data)
    assertRedirects(
        response,
        reverse('news:detail', args=[news.id]) + '#comments'
    )
    coment.refresh_from_db()
    assert coment.text == form_data['text']


def test_other_user_cant_edit_note(not_author_client, form_data, coment):
    """зарегистрированный пользователь не может редактировать чужой комент"""
    url = reverse('news:edit', args=[coment.id])
    response = not_author_client.post(url, form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Получаем новый объект запросом из БД.
    note_from_db = Comment.objects.get(id=coment.id)
    # Проверяем, что атрибуты объекта из БД равны атрибутам заметки до запроса.
    assert coment.text == note_from_db.text


def test_author_can_delete_note(author_client, coment, news):
    url = reverse('news:delete', args=[coment.id])
    response = author_client.post(url)
    assertRedirects(
        response,
        reverse('news:detail', args=[news.id]) + '#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client, coment):
    url = reverse('news:delete', args=[coment.id])
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
