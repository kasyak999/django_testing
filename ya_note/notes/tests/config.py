from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from notes.models import Note
from django.urls import reverse


User = get_user_model()


class MainConfig(TestCase):
    name_users_author = 'Лев Толстой'
    name_users_not_author = 'лев'
    title = 'Заголовок'
    text = 'Текст новости'
    slug = 'qwe'
    new_title = 'Заголовок new'
    new_text = 'Текст новости new'
    new_slug = 'qwenew'
    context_object_name = 'object_list'
    add = 'notes:add'
    list = 'notes:list'
    edit = 'notes:edit'
    delete = 'notes:delete'
    success = 'notes:success'
    detail = 'notes:detail'
    login = 'users:login'
    home = 'notes:home'
    logout = 'users:logout'
    signup = 'users:signup'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.name_users_author)
        cls.not_author = User.objects.create(
            username=cls.name_users_not_author
        )
        cls.client = Client()
        cls.client_author = Client()
        cls.client_not_author = Client()
        cls.client_author.force_login(cls.author)
        cls.client_not_author.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=cls.title, text=cls.text, slug=cls.slug,
            author=cls.author
        )
        cls.list_url = reverse(cls.list)
        cls.edit_url = reverse(cls.edit, args=(cls.note.slug,))
        cls.add_url = reverse(cls.add)
        cls.delete_url = reverse(cls.delete, args=(cls.note.slug,))
        cls.success_url = reverse(cls.success)
        cls.detail_url = reverse(cls.detail, args=(cls.note.slug,))
        cls.login_url = reverse(cls.login)
        cls.home_url = reverse(cls.home)
        cls.logout_url = reverse(cls.logout)
        cls.signup_url = reverse(cls.signup)
        cls.form_data = {
            'title': cls.new_title,
            'text': cls.new_text,
            'slug': cls.new_slug
        }
        cls.comments_count = Note.objects.count()
