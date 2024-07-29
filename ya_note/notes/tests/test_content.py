from notes.forms import NoteForm
from .config import MainConfig


class TestDetail(MainConfig):

    def test_notes(self):
        """
        отдельная заметка передаётся на страницу со списком заметок в
        списке object_list в словаре context;
        """
        response = self.client_author.get(self.list_url)
        self.assertIn(self.context_object_name, response.context)
        self.assertIn(self.note, response.context[self.context_object_name])

    def test_notes_2(self):
        """
        в список заметок одного пользователя не попадают заметки
        другого пользователя;
        """
        response = self.client_not_author.get(self.list_url)
        self.assertNotIn(self.note, response.context[self.context_object_name])

    def test_authorized_and_anonim_client_has_form(self):
        """на страницы создания и редактирования заметки передаются формы."""
        for name in (self.add_url, self.edit_url):
            with self.subTest(name=name):
                response = self.client_author.get(name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
