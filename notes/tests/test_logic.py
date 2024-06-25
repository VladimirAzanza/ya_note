from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
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
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

    def test_creation_of_unique_slug(self):
        url = reverse('notes:add')
        self.auth_client.post(url, data=self.form_data)
        notes_created = Note.objects.filter(author=self.author)
        self.assertIsNotNone(notes_created[0].slug)
        self.auth_client.post(url, data=self.form_data)
        self.assertRaises(ValidationError)

    def test_redirect_after_creation(self):
        url = reverse('notes:add')
        redirect_url = reverse('notes:success')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, redirect_url)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)


class TestNoteEditDelete(TestCase):
    NEW_TEXT = 'Text in english'
    NEW_TITLE = 'Title in english'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author
        )
        cls.another_author = User.objects.create(username='Peter Pan')
        cls.auth_author = Client()
        cls.auth_another_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.auth_another_author.force_login(cls.another_author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {
            'text': cls.NEW_TEXT,
            'title': cls.NEW_TITLE,
        }

    def test_author_edit_note(self):
        response = self.auth_author.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.title, self.NEW_TITLE)

    def test_author_delete_note(self):
        response = self.auth_author.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_another_author_edit_other_authors_note(self):
        response = self.auth_another_author.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_another_author_delete_other_authors_note(self):
        response = self.auth_another_author.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
