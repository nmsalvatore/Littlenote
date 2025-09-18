"""Integration tests for journal models."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from src.apps.journal.models import JournalEntry


User = get_user_model()


class JournalEntryTests(TestCase):
    """
    Tests for the JournalEntry model.
    """
    def setUp(self):
        self.test_user_email = "testuser@example.com"
        self.test_user = User.objects.create_user(
            username=self.test_user_email,
            email=self.test_user_email,
        )

    def test_journal_entry_creation(self):
        """
        Test that journal entry can be created.
        """
        journal_entry = JournalEntry.objects.create(
            content="What a lovely life!",
            author=self.test_user
        )
        self.assertTrue(journal_entry.id)
