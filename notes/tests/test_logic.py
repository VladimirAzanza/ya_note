from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'author': cls.author
        }

    def test_redirect_after_creation(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)
