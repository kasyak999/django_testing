from django.test import TestCase, Client
from notes.models import Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.forms import NoteForm


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
        cls.detail_url = reverse('notes:add')

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        # Делаем всё то же самое для пользователя-читателя.
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # URL для редактирования комментария.
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        # URL для удаления комментария.
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NEW_COMMENT_TEXT[0],
            'text': cls.NEW_COMMENT_TEXT[1],
            'slug': cls.NEW_COMMENT_TEXT[2]
        }

    def test_author_can_delete(self):
        # От имени автора комментария отправляем DELETE-запрос на удаление.
        response = self.auth_client.delete(self.delete_url)
        # Проверяем, что редирект привёл к разделу с комментариями.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, reverse('notes:success'))
        # Считаем количество комментариев в системе.
        comments_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(comments_count, 0)

    def test_author_can_edit(self):
        response = self.auth_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_COMMENT_TEXT[0])
        self.assertEqual(self.note.text, self.NEW_COMMENT_TEXT[1])
        self.assertEqual(self.note.slug, self.NEW_COMMENT_TEXT[2])
