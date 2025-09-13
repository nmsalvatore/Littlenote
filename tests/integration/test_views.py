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

        # Note-related URLs
        self.note_list_url = reverse("notes:list")


class NoteListTests(NoteTestCase):
    """
    Integration tests for note list page.
    """
    def test_note_list_redirects_unauthenticated_users(self):
        """
        Test that unauthenticated users are redirected to the front
        page.
        """
        response = self.client.get(self.note_list_url)
        self.assertRedirects(response, "/")

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


class NewNoteTests(NoteTestCase):
    """
    Integration tests for new note page.
    """
    def setUp(self):
        super().setUp()
        self.new_note_url = reverse("notes:new")

    def test_new_note_redirects_unauthenticated_users(self):
        """
        Test that new note route redirects unauthenticated users to the
        front page.
        """
        response = self.client.get(self.new_note_url)
        self.assertRedirects(response, "/")

    def test_new_note_accessible_to_logged_in_users(self):
        """
        Test that new note page is accessible to logged-in users.
        """
        self.client.force_login(self.test_user)
        response = self.client.get(self.new_note_url)
        self.assertEqual(response.status_code, 200)

    def test_new_note_submission_redirects_to_list(self):
        """
        Test that submission of a new note redirects the user to the
        note list page.
        """
        self.client.force_login(self.test_user)
        response = self.client.post(self.new_note_url, {
            "title": "Hello, Littlenote!",
            "content": "It's a beautiful day!"
        })
        self.assertRedirects(response, "/notes/")


class NoteDetailTests(NoteTestCase):
    """
    Integration tests for note detail page.
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
        self.assertRedirects(response, "/")

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


class NoteDeleteTests(NoteTestCase):
    """
    Integration tests for note deletion.
    """
    def setUp(self):
        super().setUp()
        self.test_note = Note.objects.get(title="Test note #1")
        self.test_note_delete_url = reverse(
            "notes:delete",
            args=[self.test_note.id]
        )

    def test_note_cannot_be_deleted_by_unauthenticated_user(self):
        """
        Test that a note CANNOT be deleted by an unauthenticated user.
        """
        self.client.post(self.test_note_delete_url)
        note = Note.objects.filter(id=self.test_note.id)
        self.assertTrue(note.exists())

    def test_note_cannot_be_deleted_by_stranger(self):
        """
        Test that a note CANNOT be deleted by a user who is not the
        author of the note.
        """
        self.client.force_login(self.strange_user)
        self.client.post(self.test_note_delete_url)
        note = Note.objects.filter(id=self.test_note.id)
        self.assertTrue(note.exists())

    def test_note_deleted_with_post_request(self):
        """
        Test that a note is successfully deleted with a POST request
        to the notes:delete URL.
        """
        self.client.force_login(self.test_user)
        self.client.post(self.test_note_delete_url)
        response = self.client.get(self.note_list_url)
        self.assertNotIn(self.test_note.title, response.text)


class NoteEditTests(NoteTestCase):
    """
    Integration tests for note edit page.
    """
    def setUp(self):
        super().setUp()
        self.test_note = Note.objects.get(title="Test note #1")
        self.note_edit_url = reverse(
            "notes:edit",
            args=[self.test_note.id]
        )

    def test_note_edit_viewable_by_author(self):
        """
        Test that the note edit page can be viewed by the note author.
        """
        self.client.force_login(self.test_user)
        response = self.client.get(self.note_edit_url)
        self.assertEqual(response.status_code, 200)

    def test_note_edit_redirects_unauthenticated_users(self):
        """
        Test that unauthenticated users are redirected from edit page.
        """
        response = self.client.get(self.note_edit_url)
        self.assertRedirects(response, "/")

    def test_note_edit_not_viewable_by_stranger(self):
        """
        Test that the note edit page CANNOT be viewed by strangers.
        """
        self.client.force_login(self.strange_user)
        response = self.client.get(self.note_edit_url)
        self.assertEqual(response.status_code, 404)

    def test_note_edit_submission_redirects_to_list(self):
        """
        Test that submission of updated note redirects the user to the
        note list.
        """
        self.client.force_login(self.test_user)
        response = self.client.post(self.note_edit_url, {
            "title": "Hello Littlenote!",
            "content": "It's a beautiful day!"
        })
        self.assertRedirects(response, "/notes/")

    def test_note_edit_updates_note(self):
        """
        Test that submission of updated note actually updates the note.
        """
        self.client.force_login(self.test_user)

        # Verify original note content
        response = self.client.get(reverse("notes:detail", args=[self.test_note.id]))
        self.assertIn("Test note #1", response.text)
        self.assertIn("Hello, test user!", response.text)

        # Update the note
        response = self.client.post(self.note_edit_url, {
            "title": "Hello Littlenote!",
            "content": "It's a beautiful day!"
        })

        # Verify new note content
        response = self.client.get(reverse("notes:detail", args=[self.test_note.id]))
        self.assertIn("Hello Littlenote!", response.text)
        self.assertIn("It's a beautiful day!", response.text)

        # Verify original note content is no longer present
        response = self.client.get(reverse("notes:detail", args=[self.test_note.id]))
        self.assertNotIn("Test note #1", response.text)
        self.assertNotIn("Hello, test user!", response.text)
