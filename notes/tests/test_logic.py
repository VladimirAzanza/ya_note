from http import HTTPStatus

from django.core.exceptions import ValidationError
from pytils.translit import slugify

from .test_common import TestCommon
from notes.models import Note


class TestNoteCreation(TestCommon):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'author': cls.author
        }

    def test_user_can_create_note(self):
        """Test that authenticated users have access to create notes."""
        note_count_before_creation = Note.objects.count()
        self.assertEqual(note_count_before_creation, 1)
        self.auth_author.post(
            self.add_note_url, data=self.form_data
        )
        note_count_after_creation = Note.objects.count()
        self.assertEqual(note_count_after_creation, 2)
        new_note = Note.objects.get(
            title=self.form_data['title'],
            text=self.form_data['text'],
            author=self.form_data['author']
        )
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.form_data['author'])

    def test_anonymous_user_cant_create_note(self):
        """Test that anonymous users do not have access to create notes."""
        note_count_before_attempt = Note.objects.count()
        self.assertEqual(note_count_before_attempt, 1)
        self.client.post(
            self.add_note_url, data=self.form_data
        )
        note_count_after_attempt = Note.objects.count()
        self.assertEqual(note_count_after_attempt, 1)

    def test_creation_of_unique_slug(self):
        """Test the creation of unique slugs for notes."""
        self.form_data['slug'] = self.note.slug
        self.auth_author.post(
            self.add_note_url, data=self.form_data
        )
        self.assertRaises(ValidationError)

    def test_empty_slug(self):
        """Test the creation of slugs using slugify method on the title."""
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        expected_slug = slugify(self.note.title)
        self.assertEqual(self.note.slug, expected_slug)


class TestNoteEditDelete(TestCommon):
    NEW_NOTE_SLUG = 'slug_in_english'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NEW_NOTE_SLUG
        }

    def test_author_edit_note(self):
        """Test that author of the note can edit it successfully."""
        self.auth_author.post(
            self.edit_note_url, data=self.form_data
        )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_author_delete_note(self):
        """Test that author of the note can delete it successfully."""
        notes_count_before_delete = Note.objects.count()
        self.assertEqual(notes_count_before_delete, 1)
        self.auth_author.delete(self.delete_url)
        notes_count_after_delete = Note.objects.count()
        self.assertEqual(notes_count_after_delete, 0)

    def test_another_author_edit_other_authors_note(self):
        """Test that a non-author cannot edit another author's note."""
        response = self.auth_reader.post(
            self.edit_note_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_another_author_delete_other_authors_note(self):
        """Test that a non-author cannot delete another author's note."""
        response = self.auth_reader.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.author, note_from_db.author)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
