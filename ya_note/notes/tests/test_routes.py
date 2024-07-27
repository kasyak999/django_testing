from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author = User.objects.create(username='Лев')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug='qwe',
            author=cls.author
        )

    def test_home_page_anonymous_user(self):
        """
        Главная страница доступна анонимному пользователю и регистрации
        пользователей, входа в учётную запись и выхода из неё доступны
        всем пользователям
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user(self):
        """
        Аутентифицированному пользователю доступна страница со списком
        заметок notes/, страница успешного добавления заметки done/, страница
        добавления новой заметки add/.
        """
        self.client.force_login(self.author)
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_redirect(self):
        """
        При попытке перейти на страницу успешного добавления записи,
        страницу добавления заметки, анонимный пользователь перенаправляется
        на страницу логина.
        """
        login_url = reverse('users:login')
        for name in (
            'notes:add', 'notes:list', 'notes:success'
        ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url, status_code=302)



    def test_anonymous_user_redirect_2(self):
        """
        При попытке перейти на страницу списка заметок, редактирования или 
        удаления заметки анонимный пользователь перенаправляется на 
        страницу логина.
        """
        login_url = reverse('users:login')
        for name in (
            'notes:edit', 'notes:delete', 'notes:detail'
        ):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_of_a_separate_note_user(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки 
        доступны только автору заметки. 
        """
        self.client.force_login(self.author)
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_of_a_separate_note_not_user(self):
        """
        Если на эти страницы попытается зайти другой 
        пользователь — вернётся ошибка 404.
        """
        self.client.force_login(self.not_author)
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
