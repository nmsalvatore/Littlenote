"""Functional tests for UI navigation."""

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from src.apps.notes.models import Note
from .helpers.interactions import UserInteractions


User = get_user_model()


class UserFlowTests(LiveServerTestCase):
    """
    Functional tests for general user flows.
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
        for num in range(1, 15):
            Note.objects.create(
                title=f"Test note #{num}",
                content="Hello, Littlenote!",
                author=self.user
            )

    def tearDown(self):
        self.browser.quit()

    def test_back_button(self):
        """
        Test that back button navigates to the last page the user
        visited.
        """
        self.browser.get(self.live_server_url)
        self.interactions.login_returning_user(self.user_email)

        self.interactions.open_note_detail(title="Test note #14")
        self.interactions.click_back_button()
        self.assertTrue(self.browser.current_url.endswith("/notes/"))

        self.interactions.click_next_page_button()
        self.interactions.open_note_detail(title="Test note #1")
        self.interactions.click_back_button()
        self.assertTrue(self.browser.current_url.endswith("/notes/?page=2"))
