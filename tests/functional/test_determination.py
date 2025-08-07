"""Functional tests for a determined user."""

from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gettext import find


class DeterminedUserTest(LiveServerTestCase):
    """
    Testing suite of a determined user who knows about Littlenote and
    is determined to use it as quickly as possible.

    Backstory:
        Danny saw someone mention how Littlenote leveled-up their
        learning 100x and is determined to get signed-up and using
        the application immediately.
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

        # A new input is rendered that is requesting a one-time passcode
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[contains(@name,'code')]")))

        self.fail("Finish the test!")
