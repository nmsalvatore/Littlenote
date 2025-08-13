"""Functional tests of user authentication flows."""

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
class LoginFlowTest(LiveServerTestCase):
    """
    Testing suite of a successful log in for a returning user.
    """

    def setUp(self) -> None:
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, timeout=5)
        self.user_email = "testuser@example.com"

    def tearDown(self) -> None:
        self.browser.quit()

    def test_login(self):
        """
        Test login flow for a returning user.
        """
        # Initialize user.
        User.objects.create_user(
            username=self.user_email,
            email=self.user_email
        )

        # User goes to home page.
        self.browser.get(self.live_server_url)

        # User submits their email address into the form.
        self._enter_email_address(self.user_email)
        self._click_continue_with_email_button()

        # User copies the passcode from their email.
        passcode = self._copy_passcode_from_email()

        # User submits passcode into the form.
        self._enter_passcode(passcode)
        self._click_login_button()

        # User should be redirected to dashboard.
        self.wait.until(EC.url_contains("/dashboard/"))

    def test_signup_and_login(self):
        """
        Test login flow for new user.
        """
        # User goes to home page.
        self.browser.get(self.live_server_url)

        # User submits their email address into the form.
        self._enter_email_address(self.user_email)
        self._click_continue_with_email_button()

        # User copies the passcode from their email.
        passcode = self._copy_passcode_from_email()

        # User submits passcode into the form.
        self._enter_passcode(passcode)
        self._click_signup_button()

        # User should be redirected to dashboard.
        self.wait.until(EC.url_contains("/dashboard/"))

    def _enter_email_address(self, email_address):
        """
        User enters their email address into the form.
        """
        email_input = self.browser.find_element(By.ID, "continue_with_email_input")
        email_input.send_keys(email_address)

    def _click_continue_with_email_button(self):
        """
        User click of the "Continue with email" button.
        """
        email_button = self.browser.find_element(By.ID, "continue_with_email_button")
        email_button.click()

    def _copy_passcode_from_email(self):
        """
        User copies passcode from email.
        """
        email_message = mail.outbox[0]
        passcode_match = re.search(r"Your one-time passcode is (\d{8})", email_message.subject)
        return passcode_match.group(1)

    def _enter_passcode(self, passcode):
        """
        User enters the passcode into the form.
        """
        passcode_input = self.wait.until(EC.presence_of_element_located((By.NAME, "passcode")))
        passcode_input.send_keys(passcode)

    def _click_login_button(self):
        """
        User clicks the login button.
        """
        login_button = self.browser.find_element(By.ID, "login_button")
        login_button.click()

    def _click_signup_button(self):
        """
        User clicks the sign-up button.
        """
        signup_button = self.browser.find_element(By.ID, "signup_button")
        signup_button.click()
