"Functional tests for user story #1"

from django.test import LiveServerTestCase

from selenium import webdriver


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
        # home page of lilnotes.app to see what all the fuss is about.
        self.browser.get(self.live_server_url)

        # He checks the title of the page to make sure it looks like
        # what he's looking for
        self.assertIn("Lil' Notes", self.browser.title)
