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
        cls.reader = User.objects.create(username='Peter Pan')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)

    def test_notes_list_for_different_user(self):
        for client, note_in_list in (
            (self.auth_author, True),
            (self.auth_reader, False),
        ):
            with self.subTest(client=client, note_in_list=note_in_list):
                url = reverse('notes:list')
                response = client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_auth_client_has_form(self):
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        ):
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.auth_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_anonymous_client_has_no_form(self):
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIsNone(response.context)
