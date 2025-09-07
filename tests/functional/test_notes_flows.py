"""Functional tests for user flows with notes."""

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .helpers.interactions import UserInteractions

class NotesFlowTest(LiveServerTestCase):
    """
    Functional tests for user flows using notes.
    """

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, timeout=5)
        self.interactions = UserInteractions(self.browser)
        self.new_user_email = "newkid@example.com"

    def tearDown(self):
        self.browser.quit()

    def test_new_user_makes_first_note(self):
        """
        Test user flow for a new user making their first note.
        """
        # User goes to home page, signs up, and logs in.
        self.browser.get(self.live_server_url)
        self.interactions.signup_and_login_new_user(self.new_user_email)

        # They're redirected to the dashboard and should see a
        # welcome message.
        self.wait.until(EC.url_contains("/notes/"))
        messages = self.browser.find_element(By.CLASS_NAME, "messages")
        self.assertIn("Welcome", messages.text)

        # They'll also see a heatmap of their activity.

        # Below the heatmap they'll see a message saying they don't
        # have any notes yet and to select the input at the bottom of
        # the page to make their first note.
        self.fail("Finish the test")
