from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

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
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.auth_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.form_data['author'])

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        redirect_url = f"{reverse('users:login')}?next={url}"
        self.assertRedirects(response, redirect_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_creation_of_unique_slug(self):
        url = reverse('notes:add')
        self.auth_author.post(url, data=self.form_data)
        self.form_data['title'] = 'New title'
        created_note = Note.objects.get()
        self.form_data['slug'] = created_note.slug
        self.auth_author.post(url, data=self.form_data)
        self.assertRaises(ValidationError)

    def test_empty_slug(self):
        url = reverse('notes:add')
        response = self.auth_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(created_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NEW_TEXT = 'Text in english'
    NEW_TITLE = 'Title in english'
    NEW_SLUG = 'slug_in_english'

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
            'slug': cls.NEW_SLUG
        }

    def test_author_edit_note(self):
        response = self.auth_author.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.slug, self.NEW_SLUG)

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
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_another_author_delete_other_authors_note(self):
        response = self.auth_another_author.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
