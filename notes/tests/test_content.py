from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm


User = get_user_model()


class TestContentForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.add_note_url = reverse('notes:add')

    def test_auth_client_has_form(self):
        response = self.auth_client.get(self.add_note_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.add_note_url)
        self.assertIsNone(response.context)
