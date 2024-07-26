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
    """Авторизованный пользователь может отправить комментарий."""
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
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=[news.id])
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'name', BAD_WORDS
)
def test_not_unique_slug(author_client, news, name):
    """
    Если комментарий содержит запрещённые слова, он не
    будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=[news.id])
    response = author_client.post(url, data={'text': name})
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


def test_author_can_edit_note(author_client, form_data, coment, news):
    """
    Авторизованный пользователь может редактироватьсвои комментарии.
    """
    url = reverse('news:edit', args=[coment.id])
    response = author_client.post(url, form_data)
    assertRedirects(
        response,
        reverse('news:detail', args=[news.id]) + '#comments'
    )
    coment.refresh_from_db()
    assert coment.text == form_data['text']


def test_other_user_cant_edit_note(not_author_client, form_data, coment):
    """
    Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    url = reverse('news:edit', args=[coment.id])
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Comment.objects.get(id=coment.id)
    assert coment.text == note_from_db.text


def test_author_can_delete_note(author_client, coment, news):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=[coment.id])
    response = author_client.post(url)
    assertRedirects(
        response,
        reverse('news:detail', args=[news.id]) + '#comments'
    )
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client, coment):
    """
    Авторизованный пользователь не может удалять
    чужие комментарии.
    """
    url = reverse('news:delete', args=[coment.id])
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
