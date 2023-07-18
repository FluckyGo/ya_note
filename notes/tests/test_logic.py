from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    TITLE_TEXT_TEST = 'Тестовый заголовок'
    TEXT_TEST = 'Тестовый текст'
    SLUG_TEST = 'slug-test'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.TITLE_TEXT_TEST,
            'text': cls.TEXT_TEST,
            'slug': cls.SLUG_TEST
        }

    def test_anonymous_user_cant_create_notes(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_comment(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, f'{self.redirect_url}')
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        notes = Note.objects.get()
        self.assertEqual(notes.text, self.TEXT_TEST)
        self.assertEqual(notes.title, self.TITLE_TEXT_TEST)
        self.assertEqual(notes.author, self.user)


class TestNoteEditDelete(TestCase):
    TITLE_TEXT_TEST = 'Тестовый заголовок'
    NEW_TITLE_TEXT_TEST = 'Новый тестовый заголовок'

    TEXT_TEST = 'Тестовый текст'
    NEW_TEXT_TEST = 'Новый тестовый текст'

    SLUG_TEST = 'slug-test'
    NEW_SLUG_TEST = 'new-slug-test'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.redirect_url = reverse('notes:success')

        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Другой юзер')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.notes = Note.objects.create(
            title=cls.TITLE_TEXT_TEST,
            text=cls.TEXT_TEST,
            slug=cls.SLUG_TEST,
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))

        cls.form_data = {
            'title': cls.NEW_TITLE_TEXT_TEST,
            'text': cls.NEW_TEXT_TEST,
            'slug': cls.NEW_SLUG_TEST
        }

    def test_author_can_delete_notes(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_notes_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_notes(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.NEW_TITLE_TEXT_TEST)
        self.assertEqual(self.notes.text, self.NEW_TEXT_TEST)
        self.assertEqual(self.notes.slug, self.NEW_SLUG_TEST)

    def test_user_cant_edit_notes_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.TITLE_TEXT_TEST)
        self.assertEqual(self.notes.text, self.TEXT_TEST)
        self.assertEqual(self.notes.slug, self.SLUG_TEST)
