from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestNotesCreateFormAvailible(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.add_url = reverse('notes:add')
        cls.author = User.objects.create(username='test')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug',
        )

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.add_url)
        self.assertIsNotNone('form', response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)


class TestListPageOrder(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='test')

        for index in range(5):
            notes = Note.objects.create(
                title=f'{index}',
                text='Текст',
                author=cls.author,
                slug=f'{index}')
            notes.save()

    def test_news_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_id = [notes.id for notes in object_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)
