from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    name_users_author = 'Лев Толстой'
    name_users_not_author = 'лев'
    title = 'Заголовок'
    text = 'Текст новости'
    slug = 'qwe'

    add = 'notes:add'
    edit = 'notes:edit'
    delete = 'notes:delete'
    success = 'notes:success'
    edit_delete_detail = ('notes:edit', 'notes:delete', 'notes:detail')
    add_list_success = ('notes:add', 'notes:list', 'notes:success')

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
        cls.login_url = reverse('users:login')

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
        for name in self.add_list_success:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_redirect(self):
        """
        При попытке перейти на страницу успешного добавления записи,
        страницу добавления заметки, анонимный пользователь перенаправляется
        на страницу логина.
        """
        for name in self.add_list_success:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url, status_code=302)

    def test_anonymous_user_redirect_2(self):
        """
        При попытке перейти на страницу списка заметок, редактирования или
        удаления заметки анонимный пользователь перенаправляется на
        страницу логина.
        """
        for name in self.edit_delete_detail:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_of_a_separate_note_user(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки.
        """
        for name in self.edit_delete_detail:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_of_a_separate_note_not_user(self):
        """
        Если на эти страницы попытается зайти другой
        пользователь — вернётся ошибка 404.
        """
        for name in self.edit_delete_detail:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client_not_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
