"""Functional tests of notes app interactions."""

import time

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from src.apps.notes.models import Note
from .helpers.interactions import UserInteractions


User = get_user_model()


class NoteDeleteFlow(StaticLiveServerTestCase):
    """
    Functional tests of note deletion flow.
    """
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, timeout=5)
        self.interactions = UserInteractions(self.browser)

        # Create a test user
        self.user_email = "testuser@example.com"
        self.user = User.objects.create_user(
            username=self.user_email,
            email=self.user_email
        )

        # Create some test data
        for num in range(1, 4):
            Note.objects.create(
                title=f"Test note #{num}",
                content="Hello, Littlenote!",
                author=self.user
            )

    def tearDown(self):
        self.browser.quit()

    def test_note_delete_with_modal(self):
        """
        Test that user successfully deletes a note from the note
        deletion dialog.
        """
        self.browser.get(self.live_server_url)
        self.interactions.login_returning_user(self.user_email)
        self.interactions.open_note_detail(title="Test note #1")
        self.interactions.open_note_delete_dialog()
        self.interactions.confirm_note_delete()
        self.assertNotIn("Test note #1", self.browser.page_source)
