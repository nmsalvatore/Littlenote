"""Integration tests for views."""


from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls import reverse

from src.apps.notes.models import Note


User = get_user_model()


class NoteTestCase(TestCase):
    """
    Extended class for note-related tests. Includes creation of two
    users, each with their own set up notes.
    """
    def setUp(self):
        # Create a test user
        self.test_user_email = "testuser@example.com"
        self.test_user = User.objects.create_user(
            username=self.test_user_email,
            email=self.test_user_email
        )

        # Create a strange user
        self.strange_user_email = "strangeuser@example.com"
        self.strange_user = User.objects.create_user(
            username=self.strange_user_email,
            email=self.strange_user_email
        )

        # Generate test user's notes
        for num in range(1, 4):
            Note.objects.create(
                title=f"Test note #{num}",
                content="Hello, test user!",
                author=self.test_user
            )

        # Generate strange user's notes
        for num in range(1, 4):
            Note.objects.create(
                title=f"Strange note #{num}",
                content="Hello, stranger!",
                author=self.strange_user
            )


class NoteListViewTests(NoteTestCase):
    """
    Integration tests for NoteListView.
    """
    def setUp(self):
        super().setUp()
        self.note_list_url = reverse("notes:list")

    def test_note_list_redirects_unauthenticated_users(self):
        """
        Test that unauthenticated users are redirected to the front
        page.
        """
        response = self.client.get(self.note_list_url)
        self.assertRedirects(response, "/?next=/notes/")

    def test_note_list_requires_login(self):
        """
        Test that the note list can only be accessed by authenticated
        users.
        """
        self.client.force_login(self.test_user)
        response = self.client.get(self.note_list_url)
        self.assertEqual(response.status_code, 200)

    def test_note_list_shows_user_notes(self):
        """
        Test that the note list shows notes authored by the
        logged-in user.
        """
        self.client.force_login(self.test_user)
        response = self.client.get(self.note_list_url)
        self.assertIn("Test note #1", response.text)
        self.assertIn("Test note #2", response.text)
        self.assertIn("Test note #3", response.text)

    def test_note_list_does_not_show_strange_notes(self):
        """
        Test that the note list does NOT show notes authored by
        strangers.
        """
        self.client.force_login(self.test_user)
        response = self.client.get(self.note_list_url)
        self.assertNotIn("Strange note #1", response.text)
        self.assertNotIn("Strange note #2", response.text)
        self.assertNotIn("Strange note #3", response.text)


class NewNoteViewTests(TestCase):
    """
    Integration tests for NewNoteView.
    """
    def test_new_note_requires_auth(self):
        """
        Test that new note page only accessible to authenticated users.
        """
        response = self.client.get(reverse("notes:new"))
        self.assertRedirects(response, "/?next=/notes/new/")


class NoteDetailViewTests(NoteTestCase):
    """
    Integration tests for NoteDetailView.
    """
    def setUp(self):
        super().setUp()
        self.test_note = Note.objects.get(title="Test note #1")
        self.test_note_detail_url = reverse("notes:detail", args=[self.test_note.id])

    def test_note_detail_redirects_unauthenticated_users(self):
        """
        Test that note detail redirects unauthenticated users
        """
        response = self.client.get(self.test_note_detail_url)
        self.assertRedirects(response, f"/?next=/notes/{self.test_note.id}/")

    def test_note_detail_viewable_by_author(self):
        """
        Test that note detail is viewable by the note author.
        """
        self.client.force_login(self.test_user)
        user = get_user(self.client)
        self.assertEqual(user, self.test_note.author)
        response = self.client.get(self.test_note_detail_url)
        self.assertEqual(response.status_code, 200)

    def test_note_detail_not_viewable_by_stranger(self):
        """
        Test that note detail is NOT viewable by a stranger
        (non-author). User should see a 404 page.
        """
        self.client.force_login(self.strange_user)
        user = get_user(self.client)
        self.assertNotEqual(user, self.test_note.author)
        response = self.client.get(self.test_note_detail_url)
        self.assertEqual(response.status_code, 404)
