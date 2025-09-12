"""Integration tests for models."""

import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase

from src.apps.notes.models import Note


User = get_user_model()


class NoteModelTestCase(TestCase):
    """
    Integration tests for the Note model.
    """
    def setUp(self):
        self.user_email = "testuser@example.com"
        self.user = User.objects.create_user(
            username=self.user_email,
            email=self.user_email
        )

    def test_user_note_creation(self):
        """
        Test that note can be created and is in database.
        """
        note = Note.objects.create(
            title="Hello world",
            content="Welcome to Littlenote",
            author=self.user
        )
        saved_note = Note.objects.get(id=note.id)
        self.assertEqual(note.title, saved_note.title)
        self.assertEqual(note.content, saved_note.content)
        self.assertEqual(note.author, self.user)

    def test_note_uses_uuid(self):
        """
        Test that note uses a UUID in ID field.
        """
        note = Note.objects.create(
            title="Hello world",
            content="Welcome to Littlenote",
            author=self.user
        )
        self.assertEqual(type(note.id), uuid.UUID)
        self.assertEqual(len(str(note.id)), 36)
