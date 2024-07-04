from http import HTTPStatus

from django.urls import reverse

from .test_common import TestCommon


class TestRoutes(TestCommon):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.public_urls = (
            'users:login',
            'users:logout',
            'users:signup',
            'notes:home'
        )
        cls.private_auth_urls = (
            'notes:add',
            'notes:list',
            'notes:success',
        )
        cls.author_notes_urls = (
            ('notes:edit', (cls.note.slug,)),
            ('notes:detail', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )
        cls.all_notes_urls = tuple(
            (name, None) for name in cls.private_auth_urls
        ) + cls.author_notes_urls

    def test_authentification_pages_availability(self):
        """
        Test the availability of public pages by checking their HTTP
        status code.
        """
        for name in self.public_urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Test the availability of private pages by checking their HTTP
        status code.
        """
        for name in self.private_auth_urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.auth_reader.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_pages_for_diferent_auth_user(self):
        """
        Test if the pages associated with author notes are correctly
        accessible to edit or delete by the author and return a 404
        status for unauthorized not author users.
        """
        for user, status_code in (
            (self.auth_author, HTTPStatus.OK),
            (self.auth_reader, HTTPStatus.NOT_FOUND)
        ):
            with self.subTest(user=user, status_code=status_code):
                for name, args in self.author_notes_urls:
                    with self.subTest(name=name, args=args):
                        url = reverse(name, args=args)
                        response = user.get(url)
                        self.assertEqual(response.status_code, status_code)

    def test_redirect_for_anonymous_client(self):
        """
        Test the redirection to login page when anonymous users try to
        enter private URLs.
        """
        for name, args in self.all_notes_urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f"{self.login_url}?next={url}"
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
