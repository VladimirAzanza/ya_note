from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestCommon(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    AUTHOR_USERNAME = 'Лев Толстой'
    READER_USERNAME = 'Peter Pan'
    NEW_NOTE_TEXT = 'Text in english'
    NEW_NOTE_TITLE = 'Title in english'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=cls.AUTHOR_USERNAME)
        cls.reader = User.objects.create(username=cls.READER_USERNAME)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, author=cls.author
        )
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.login_url = reverse('users:login')
        cls.list_notes_url = reverse('notes:list')
        cls.add_note_url = reverse('notes:add', args=None)
        cls.edit_note_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_note_url = reverse('notes:success')
