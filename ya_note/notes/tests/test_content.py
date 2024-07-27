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
        cls.not_author = User.objects.create(username='Лев')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug='qwe',
            author=cls.author
        )
        cls.detail_url = reverse('notes:add')

    def test_notes(self):
        """
        отдельная заметка передаётся на страницу со списком заметок в
        списке object_list в словаре context;
        """
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn('object_list', response.context)
        self.assertIn(self.note, response.context['object_list'])

    def test_notes_2(self):
        """
        в список заметок одного пользователя не попадают заметки
        другого пользователя;
        """
        url = reverse('notes:list')
        self.client.force_login(self.not_author)
        response = self.client.get(url)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_authorized_and_anonim_client_has_form(self):
        """на страницы создания и редактирования заметки передаются формы."""
        self.client.force_login(self.author)
        for name, args in [
            ('notes:add', None), ('notes:edit', (self.note.slug,))
        ]:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
