from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContentForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.add_note_url = reverse('notes:add')
        cls.note_list_url = reverse('notes:list')

    def test_notes_list_for_different_user(self):
        reader = User.objects.create(username='Peter Pan')
        self.client.force_login(reader)
        available_urls = (
            (self.auth_author, True),
            (self.client, False),
        )
        for client, note_in_list in available_urls:
            with self.subTest(client=client, note_in_list=note_in_list):
                response = client.get(self.note_list_url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_auth_client_has_form(self):
        response = self.auth_author.get(self.add_note_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.add_note_url)
        self.assertIsNone(response.context)
