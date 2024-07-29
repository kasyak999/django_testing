from notes.models import Note
from notes.forms import WARNING
from http import HTTPStatus
from pytils.translit import slugify
from .config import MainConfig


class TestDetail(MainConfig):

    def test_author_can_add(self):
        """Залогиненный пользователь может создать заметку"""
        response = self.client_author.post(
            self.add_url, data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), self.comments_count + 1)

    def test_anonim_can_add(self):
        """анонимный пользователь не может оставлять заметки."""
        self.client.post(self.add_url, data=self.form_data)
        self.assertEqual(Note.objects.count(), self.comments_count)

    def test_impossible_to_create_identical_slag(self):
        """Невозможно создать две заметки с одинаковым slug."""
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
        self.assertEqual(Note.objects.count(), self.comments_count)

    def test_processing_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify.
        """
        self.form_data['slug'] = ''
        self.client_author.post(
            self.add_url, data=self.form_data
        )
        self.assertEqual(Note.objects.count(), self.comments_count + 1)
        created_note = Note.objects.get(title=self.form_data['title'])
        slug = slugify(self.form_data['title'])[:100]
        self.assertEqual(created_note.slug, slug)

    def test_not_author_can_delete(self):
        """Пользователь не может удалять чужие заметки"""
        response = self.client_not_author.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), self.comments_count)

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
        self.assertEqual(Note.objects.count(), self.comments_count - 1)

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
