from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note
from pytest_django.asserts import assertRedirects 


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug='qwe',
            author=cls.author
        )

    def test_pages_availability(self):
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

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in (
            'notes:edit', 'notes:delete', 'notes:detail'
        ):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_edit_and_delete(self):
        self.client.force_login(self.author)
        for name in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client_2(self):
        login_url = reverse('users:login')
        for name in (
            'notes:add', 'notes:list', 'notes:success'
        ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url, status_code=302)

    def test_availability_for_edit_and_delete_2(self):
        self.client.force_login(self.author)
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
