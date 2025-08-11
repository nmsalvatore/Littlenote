"""Test successful login for returning user."""

import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.apps.pages.constants import SuccessMessages



User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    RATELIMIT_ENABLE=False
)
class SuccessfulLoginTest(LiveServerTestCase):
    """
    Testing suite of a successful log in for a returning user.
    """

    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, timeout=5)

    def tearDown(self) -> None:
        self.browser.quit()

    def test_user_story(self):
        self.user_email = "testuser@example.com"

        # Create existing user.
        User.objects.create_user(
            username=self.user_email,
            email=self.user_email
        )

        # User goes to the Littlenote home page.
        self.browser.get(self.live_server_url)

        # They enter their email in the email input box.
        email_input = self.browser.find_element(By.ID, "continue_with_email_input")
        email_input.send_keys(self.user_email)

        # They click the button that reads "Continue with email"
        email_button = self.browser.find_element(By.ID, "continue_with_email_button")
        email_button.click()

        # They wait for the passcode form to render.
        passcode_input = self.wait.until(EC.presence_of_element_located((By.NAME, "passcode")))

        # They check for a new email from Littlenote that says
        # something about a passcode.
        self.assertEqual(len(mail.outbox), 1)
        email_message = mail.outbox[0]
        self.assertIn("littlenote", email_message.from_email.lower())
        self.assertIn("passcode", email_message.subject.lower())

        # They verify that a passcode is in the email and copy it.
        passcode_match = re.search(r"Your one-time passcode is (\d{8})", email_message.subject)
        self.assertIsNotNone(passcode_match, "Passcode not found in email subject")
        passcode = passcode_match.group(1)

        # They enter the passcode into the form and click the "Log in" button.
        passcode_input.send_keys(passcode)
        login_button = self.browser.find_element(By.ID, "login_button")
        login_button.click()

        # They are redirected to the dashboard.
        self.wait.until(EC.url_contains("/dashboard/"))

        # They should NOT see a welcome message.
        self.assertNotIn(SuccessMessages.WELCOME_NEW_USER, self.browser.page_source)

        # They see their email displayed on the dashboard.
        self.assertIn(self.user_email, self.browser.page_source)
