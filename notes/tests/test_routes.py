from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Author user')
        cls.reader = User.objects.create(username='Reader user')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_home_page(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_detail_page(self):
        url = reverse('notes:detail', args=(self.notes.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in (
                'notes:edit', 'notes:detail', 'notes:detele', 'notes:list'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.pk,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
