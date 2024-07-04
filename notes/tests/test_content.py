from .test_common import TestCommon
from notes.forms import NoteForm


class TestContentForm(TestCommon):
    def test_notes_list_for_different_user(self):
        """Test visibility of notes only by the author of the notes."""
        for client, note_in_list in (
            (self.auth_author, True),
            (self.auth_reader, False),
        ):
            with self.subTest(client=client, note_in_list=note_in_list):
                response = client.get(self.list_notes_url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_auth_client_has_form(self):
        """Test visibility of note form only by the authenticated users."""
        for url in (self.add_note_url, self.edit_note_url):
            with self.subTest(url=url):
                response = self.auth_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_anonymous_client_has_no_form(self):
        """Test that anonymous users do not have access to the note form."""
        response = self.client.get(self.add_note_url)
        self.assertIsNone(response.context)
