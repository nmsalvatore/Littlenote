"""Functional tests of user authentication flows."""

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase, override_settings

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .helpers.interactions import UserInteractions

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    RATELIMIT_ENABLE=False
)
class AuthFlowTest(LiveServerTestCase):
    """
    Functional tests for authentication of new or returning users.
    """

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.wait = WebDriverWait(self.browser, timeout=5)
        self.interactions = UserInteractions(self.browser)
        self.user_email = "testuser@example.com"

    def tearDown(self):
        self.browser.quit()

    def test_login(self):
        """
        Test login flow for a returning user.
        """
        User.objects.create_user(
            username=self.user_email,
            email=self.user_email
        )

        self.browser.get(self.live_server_url)
        self.interactions.login_returning_user(self.user_email)
        self.wait.until(EC.url_contains("/notes/"))

    def test_signup_and_login(self):
        """
        Test login flow for new user.
        """
        self.browser.get(self.live_server_url)
        self.interactions.signup_and_login_new_user(self.user_email)
        self.wait.until(EC.url_contains("/notes/"))
