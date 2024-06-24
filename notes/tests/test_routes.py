from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )

    def test_auth_urls(self):
        urls = (
            'users:login', 'users:logout', 'users:signup'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_route(self): #aqui revisar edit note delete para solo el usuario
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
