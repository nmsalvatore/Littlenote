"""Integration tests for views."""


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from src.apps.notes.models import Note


User = get_user_model()


class NoteListViewTestCase(TestCase):
    """
    Integration tests for note-related views.
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

        # Note-related URLs
        self.note_list_url = reverse("notes:list")

    def test_unauthenticated_user_redirected(self):
        """
        Test that unauthenticated users are redirected to the front
        page.
        """
        response = self.client.get(self.note_list_url)
        self.assertRedirects(response, "/?next=/notes/")

    def test_list_shows_only_user_notes(self):
        """
        Test that the note list only shows notes authored by the
        logged-in user.
        """
        self.client.force_login(self.test_user)
        response = self.client.get(self.note_list_url)

        # Test user notes should be in list
        self.assertIn("Test note #1", response.text)
        self.assertIn("Test note #2", response.text)
        self.assertIn("Test note #3", response.text)

        # Stranger notes should NOT be in list
        self.assertNotIn("Strange note #1", response.text)
        self.assertNotIn("Strange note #2", response.text)
        self.assertNotIn("Strange note #3", response.text)
