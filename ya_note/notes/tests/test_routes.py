from http import HTTPStatus
from .config import MainConfig


class TestRoutes(MainConfig):

    def test_home_page_anonymous_user(self):
        """
        Главная страница доступна анонимному пользователю и регистрации
        пользователей, входа в учётную запись и выхода из неё доступны
        всем пользователям
        """
        for name in (
            self.login_url, self.home_url, self.logout_url, self.signup_url
        ):
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_user(self):
        """
        Аутентифицированному пользователю доступна страница со списком
        заметок notes/, страница успешного добавления заметки done/, страница
        добавления новой заметки add/.
        """
        for name in (
            self.add_url, self.list_url, self.success_url,
            self.edit_url, self.delete_url, self.detail_url
        ):
            with self.subTest(name=name):
                response = self.client_author.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_user_redirect(self):
        """
        При попытке перейти на страницу успешного добавления записи,
        страницу добавления заметки, анонимный пользователь перенаправляется
        на страницу логина.
        """
        for name in (
            self.add_url, self.list_url, self.success_url,
            self.edit_url, self.delete_url, self.detail_url
        ):
            with self.subTest(name=name):
                redirect_url = f'{self.login_url}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)

    def test_pages_of_a_separate_note_not_user(self):
        """
        Если на эти страницы попытается зайти другой
        пользователь — вернётся ошибка 404.
        """
        for name in (self.edit_url, self.delete_url, self.detail_url):
            with self.subTest(name=name):
                response = self.client_not_author.get(name)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
