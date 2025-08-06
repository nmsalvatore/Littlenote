"Functional tests for user story #1"

from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By


class CuriousUserTest(LiveServerTestCase):
    """
    Testing suite for user story of a curious person who wants to check out the
    application before registering.
    """

    def setUp(self) -> None:
        self.browser = webdriver.Firefox()

    def tearDown(self) -> None:
        self.browser.quit()

    def test_curious_user_story(self):
        # George (because curious, of course) decides to check out the
        # Littlenote website to see what all the fuss is about.
        self.browser.get(self.live_server_url)

        # He checks the title of the page to make sure it looks like
        # what he's looking for.
        self.assertIn("littlenote", self.browser.title.lower())

        # He sees a call to action
        cta_button = self.browser.find_element(By.CSS_SELECTOR, "a.cta-btn")
        self.assertIn("sign up", cta_button.text.lower())

        # Being the curious boy George is, he looks around to see if
        # he can see how Littlenote works before signing up.
        nav_links = self.browser.find_elements(By.CSS_SELECTOR, "nav > menu a")
        self.assertTrue(any([link.text == "How it works" for link in nav_links]))
