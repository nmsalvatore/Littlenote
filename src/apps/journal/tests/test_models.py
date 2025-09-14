"""Integration tests for journal models."""

from django.test import TestCase

from src.apps.journal.models import JournalEntry


class JournalEntryTests(TestCase):
    """
    Tests for the JournalEntry model.
    """

    def test_journal_entry_creation(self):
        """
        Test that journal entry can be created.
        """
        journal_entry = JournalEntry.objects.create(content="What a lovely life!")
        self.assertTrue(journal_entry.id)
