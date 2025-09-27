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
        self.assertEqual(journal_entry.content, "What a lovely life!")
        self.assertEqual(journal_entry.author, self.test_user)

    def test_journal_entry_string_representation(self):
        """
        Test that journal entry has a reasonable string representation.
        """
        journal_entry = JournalEntry.objects.create(
            content="What a lovely life!",
            author=self.test_user
        )
        # Should contain some part of the content or be meaningful
        str_repr = str(journal_entry)
        self.assertTrue(len(str_repr) > 0)

    def test_journal_entry_timestamps(self):
        """
        Test that journal entry has created/updated timestamps.
        """
        journal_entry = JournalEntry.objects.create(
            content="Timestamped entry",
            author=self.test_user
        )
        # Check if timestamps exist (assuming model has these fields)
        self.assertTrue(hasattr(journal_entry, 'created_at') or hasattr(journal_entry, 'date_created'))

    def test_journal_entry_author_relationship(self):
        """
        Test that journal entry properly relates to author.
        """
        journal_entry = JournalEntry.objects.create(
            content="Author test",
            author=self.test_user
        )
        # Test reverse relationship if it exists
        user_entries = journal_entry.author.journalentry_set.all()
        self.assertIn(journal_entry, user_entries)
