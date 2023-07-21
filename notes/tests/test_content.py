from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestNotesCreateFormAvailible(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.author = User.objects.create(username='test')
        cls.reader = User.objects.create(username='Reader user')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug',
        )

    def test_anonymous_client_has_no_add_form(self):
        response = self.client.get(self.add_url)
        self.assertIsNotNone('form', response.context)

    def test_authorized_client_has_add_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)

    def test_edit_note_page_contains_form(self):
        self.edit_url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)

    def test_note_in_list_for_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)


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

    def test_notes_order(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        object_list = response.context['object_list']
        all_id = [notes.id for notes in object_list]
        sorted_id = sorted(all_id)
        self.assertEqual(all_id, sorted_id)
