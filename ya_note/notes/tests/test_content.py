from django.test import TestCase, Client
from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm


User = get_user_model()


class TestDetailPage(TestCase):
    name_users_author = 'Лев Толстой'
    name_users_not_author = 'лев'
    title = 'Заголовок'
    text = 'Текст новости'
    slug = 'qwe'
    context_object_name = 'object_list'
    add_url = 'notes:add'
    list_utl = 'notes:list'
    edit_url = 'notes:edit'

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
            title=cls.title, text=cls.text, slug=cls.slug,
            author=cls.author
        )
        cls.rev_list_utl = reverse(cls.list_utl)

    def test_notes(self):
        """
        отдельная заметка передаётся на страницу со списком заметок в
        списке object_list в словаре context;
        """
        response = self.client_author.get(self.rev_list_utl)
        self.assertIn(self.context_object_name, response.context)
        self.assertIn(self.note, response.context[self.context_object_name])

    def test_notes_2(self):
        """
        в список заметок одного пользователя не попадают заметки
        другого пользователя;
        """
        response = self.client_not_author.get(self.rev_list_utl)
        self.assertNotIn(self.note, response.context[self.context_object_name])

    def test_authorized_and_anonim_client_has_form(self):
        """на страницы создания и редактирования заметки передаются формы."""
        for name, args in [
            (self.add_url, None), (self.edit_url, (self.note.slug,))
        ]:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
