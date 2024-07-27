from django.test import TestCase
from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm


User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug='qwe',
            author=cls.author
        )
        cls.detail_url = reverse('notes:add')

    def test_authorized_client_has_form(self):
        """
        на странице создания заметки передаются формы.
        """
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
    
    def test_authorized_client_has_form_2(self):
        """
        на странице редактирования заметки передаются формы.
        """
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_unauthorized_client_gets_404(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 302)
