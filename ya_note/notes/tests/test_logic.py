from django.test import TestCase, Client
from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import WARNING
from http import HTTPStatus
from pytils.translit import slugify


User = get_user_model()


class TestDetailPage(TestCase):
    name_users_author = 'Лев Толстой'
    name_users_not_author = 'лев'
    title = 'Заголовок'
    text = 'Текст новости'
    slug = 'qwe'
    new_title = 'Заголовок new'
    new_text = 'Текст новости new'
    new_slug = 'qwenew'
    add = 'notes:add'
    edit = 'notes:edit'
    delete = 'notes:delete'
    success = 'notes:success'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.name_users_author)
        cls.not_author = User.objects.create(
            username=cls.name_users_not_author
        )
        cls.client_author = Client()
        cls.client_not_author = Client()
        cls.client_author.force_login(cls.author)
        cls.client_not_author.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=cls.title, text=cls.text,
            slug=cls.slug, author=cls.author
        )
        cls.add_url = reverse(cls.add)
        cls.edit_url = reverse(cls.edit, args=(cls.note.slug,))
        cls.delete_url = reverse(cls.delete, args=(cls.note.slug,))
        cls.success_url = reverse(cls.success)
        cls.form_data = {
            'title': cls.new_title,
            'text': cls.new_text,
            'slug': cls.new_slug
        }

    def test_author_can_add(self):
        """Залогиненный пользователь может создать заметку"""
        initial_count = Note.objects.count()
        response = self.client_author.post(
            self.add_url, data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, initial_count + 1)

    def test_anonim_can_add(self):
        """анонимный пользователь не может оставлять заметки."""
        client = Client()
        initial_count = Note.objects.count()
        client.post(self.add_url, data=self.form_data)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, initial_count)

    def test_impossible_to_create_identical_slag(self):
        """Невозможно создать две заметки с одинаковым slug."""
        initial_count = Note.objects.count()
        self.form_data['slug'] = self.slug
        response = self.client_author.post(
            self.add_url, data=self.form_data
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
        self.client_author.post(
            self.add_url, data=self.form_data
        )
        self.assertEqual(Note.objects.count(), count + 1)
        created_note = Note.objects.get(title=self.form_data['title'])
        slug = slugify(self.form_data['title'])[:100]
        self.assertEqual(created_note.slug, slug)

    def test_not_author_can_delete(self):
        """Пользователь не может удалять чужие заметки"""
        response = self.client_not_author.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_author_can_edit(self):
        """Пользователь не может редактировать чужие заметки"""
        response = self.client_not_author.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, self.new_title)
        self.assertNotEqual(self.note.text, self.new_text)
        self.assertNotEqual(self.note.slug, self.new_slug)

    def test_author_can_delete(self):
        """Пользователь может удалять свои заметки"""
        response = self.client_author.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_author_can_edit(self):
        """Пользователь может редактировать свои заметки"""
        response = self.client_author.post(
            self.edit_url, data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.new_title)
        self.assertEqual(self.note.text, self.new_text)
        self.assertEqual(self.note.slug, self.new_slug)
