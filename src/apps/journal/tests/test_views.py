"""Integration tests for journal views."""


from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse

from src.apps.journal.models import JournalEntry


User = get_user_model()


class JournalEntryListViewTests(LiveServerTestCase):
    """
    Tests for JournalEntryListView.
    """

    def setUp(self):
        self.new_journal_entry_url = reverse("journal:new-entry")
        self.test_user_email = "testuser@example.com"
        self.test_user = User.objects.create_user(
            username=self.test_user_email,
            email=self.test_user_email
        )

    def test_journal_entry_creation_with_post(self):
        """
        Test that journal entry can be created with a POST request and
        can be successfully queried in the database.
        """
        self.client.force_login(self.test_user)
        self.client.post(self.new_journal_entry_url, {
            "content": "Stuff is weird",
        })
        self.assertTrue(JournalEntry.objects.filter(content="Stuff is weird").exists())

    def test_journal_entry_listed_after_creation(self):
        """
        Test that journal entry is shown in the journal after it has
        been created.
        """
        # login user
        # go to journal page
        # submit a journal entry
        # check if journal entry is in journal
        pass
