"""Functional tests for a determined user."""

import re
import time

from django.core import mail
from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class UserSignUpTest(LiveServerTestCase):
    """
    Testing suite of a successful user sign up.

    Backstory:
        Danny saw someone mention how Littlenote leveled-up their
        learning 100x and is determined to get signed-up as soon as
        possible.
    """

    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, timeout=5)

    def tearDown(self) -> None:
        self.browser.quit()

    def test_user_story(self):
        # He goes to the Littlenote homepage.
        self.browser.get(self.live_server_url)

        # He enters his email in the email input box.
        email_input = self.browser.find_element(By.ID, "continue_with_email_input")
        email_input.send_keys("danny@example.com")

        # He clicks the button that reads "Continue with email"
        email_button = self.browser.find_element(By.ID, "continue_with_email_button")
        email_button.click()

        # A new input is rendered that is requesting a one-time passcode.
        passcode_input = self.wait.until(EC.presence_of_element_located((By.NAME, "passcode")))

        # He checks for a new email that says something about a passcode from Littlenote.
        self.assertEqual(len(mail.outbox), 1)
        email_message = mail.outbox[0]
        self.assertIn("littlenote", email_message.from_email.lower())
        self.assertIn("passcode", email_message.subject.lower())

        # He verifies that the passcode is included in the email and
        # copies it.
        passcode_match = re.search(r"Your one-time passcode is (\d{6})", email_message.subject)
        self.assertIsNotNone(passcode_match, "Passcode not found in email subject")
        passcode = passcode_match.group(1)  # copy, beep boop beep

        # He enters the passcode into the form and clicks the sign up button
        passcode_input.send_keys(passcode)
        signup_button = self.browser.find_element(By.ID, "signup_button")
        signup_button.click()

        # He is redirected to the dashboard
        self.wait.until(EC.url_contains("/dashboard/"))

        # He sees a welcome message
        self.assertIn("Welcome to Littlenote!", self.browser.page_source)

        # He sees his email displayed on the dashboard
        self.assertIn("danny@example.com", self.browser.page_source)
