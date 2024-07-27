from django.test import TestCase, Client
from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import WARNING
from http import HTTPStatus
from pytils.translit import slugify


User = get_user_model()


class TestDetailPage(TestCase):
    COMMENT_TEXT = [
        'Заголовок',
        'Текст комментария',
        'qwe'
    ]
    NEW_COMMENT_TEXT = [
        'Обновлённый комментарий',
        'Текст комментария Обновлённый',
        'qweasd'
    ]

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title=cls.COMMENT_TEXT[0], text=cls.COMMENT_TEXT[1],
            slug=cls.COMMENT_TEXT[2], author=cls.author
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_COMMENT_TEXT[0],
            'text': cls.NEW_COMMENT_TEXT[1],
            'slug': cls.NEW_COMMENT_TEXT[2]
        }

    def test_author_can_add(self):
        """Залогиненный пользователь может создать заметку"""
        initial_count = Note.objects.count()
        response = self.auth_client.post(
            reverse('notes:add'), data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, initial_count + 1)

    def test_anonim_can_add(self):
        """анонимный пользователь не может оставлять заметки."""
        client = Client()
        initial_count = Note.objects.count()
        client.post(reverse('notes:add'), data=self.form_data)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, initial_count)

    def test_impossible_to_create_identical_slag(self):
        """Невозможно создать две заметки с одинаковым slug."""
        initial_count = Note.objects.count()
        self.form_data['slug'] = self.COMMENT_TEXT[2]
        response = self.auth_client.post(
            reverse('notes:add'), data=self.form_data
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.form_data['slug'] + WARNING
        )
        count = Note.objects.count()
        self.assertEqual(initial_count, count)

    def test_processing_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        count = Note.objects.count()
        self.form_data['slug'] = ''
        self.auth_client.post(
            reverse('notes:add'), data=self.form_data
        )
        count_2 = Note.objects.count()
        self.assertEqual(count_2, count + 1)
        created_note = Note.objects.get(title=self.form_data['title'])
        slug = slugify(self.form_data['title'])[:100]
        self.assertEqual(created_note.slug, slug)

    def test_not_author_can_delete(self):
        """Пользователь не может удалять чужие заметки"""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 1)

    def test_not_author_can_edit(self):
        """Пользователь может редактировать чужие заметки"""
        response = self.reader_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.NEW_COMMENT_TEXT[0])
        self.assertNotEqual(self.note.text, self.NEW_COMMENT_TEXT[1])
        self.assertNotEqual(self.note.slug, self.NEW_COMMENT_TEXT[2])

    def test_author_can_delete(self):
        """Пользователь может удалять свои заметки"""
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, 0)

    def test_author_can_edit(self):
        """Пользователь может редактировать свои заметки"""
        response = self.auth_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_COMMENT_TEXT[0])
        self.assertEqual(self.note.text, self.NEW_COMMENT_TEXT[1])
        self.assertEqual(self.note.slug, self.NEW_COMMENT_TEXT[2])
