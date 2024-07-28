from pytest_django.asserts import assertRedirects, assertFormError
from news.models import Comment
import pytest
from news.forms import BAD_WORDS, WARNING
from http import HTTPStatus


def test_user_can_create_news_coment(
    author_client, news, urls, author, form_data
):
    """Авторизованный пользователь может отправить комментарий."""
    count = Comment.objects.count()
    response = author_client.post(urls['detail'], data=form_data)
    assertRedirects(
        response,
        urls['detail'] + '#comments'
    )
    assert Comment.objects.count() == count + 1
    new_note = Comment.objects.get(text=form_data['text'])
    assert new_note.text == form_data['text']
    assert new_note.news == news
    assert new_note.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data, urls):
    """Анонимный пользователь не может отправить комментарий."""
    count = Comment.objects.count()
    response = client.post(urls['detail'], data=form_data)
    expected_url = f"{urls['login']}?next={urls['detail']}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == count


@pytest.mark.parametrize(
    'name', BAD_WORDS
)
def test_not_unique_slug(author_client, urls, name):
    """
    Если комментарий содержит запрещённые слова, он не
    будет опубликован, а форма вернёт ошибку.
    """
    count = Comment.objects.count()
    response = author_client.post(urls['detail'], data={'text': name})
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == count


def test_author_can_edit_note(author_client, form_data, urls, coment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(urls['edit'], form_data)
    assertRedirects(response, urls['detail'] + '#comments')
    coment.refresh_from_db()
    assert coment.text == form_data['text']


def test_other_user_cant_edit_note(not_author_client, form_data, coment, urls):
    """
    Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    response = not_author_client.post(urls['edit'], form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Comment.objects.get(id=coment.id)
    assert coment.text == note_from_db.text


def test_author_can_delete_note(author_client, urls):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.post(urls['delete'])
    assertRedirects(response, urls['detail'] + '#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client, urls):
    """
    Авторизованный пользователь не может удалять
    чужие комментарии.
    """
    response = not_author_client.post(urls['delete'])
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
