from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author = User.objects.create(username='Peter Pan')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.auth_not_author = Client()
        cls.auth_not_author.force_login(cls.not_author)

    def test_authentification_pages_availability(self):
        for name in (
            'users:login',
            'users:logout',
            'users:signup',
            'notes:home'
        ):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        for name in ('notes:add', 'notes:list', 'notes:success'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.auth_not_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_pages_for_diferent_auth_user(self):
        for user, status_code in (
            (self.auth_author, HTTPStatus.OK),
            (self.auth_not_author, HTTPStatus.NOT_FOUND)
        ):
            with self.subTest(user=user, status_code=status_code):
                for name, args in (
                    ('notes:edit', (self.note.slug,)),
                    ('notes:detail', (self.note.slug,)),
                    ('notes:delete', (self.note.slug,)),
                ):
                    with self.subTest(name=name, args=args):
                        url = reverse(name, args=args)
                        response = user.get(url)
                        self.assertEqual(response.status_code, status_code)

    def test_redirect_for_anonymous_client(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None)
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f"{reverse('users:login')}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
