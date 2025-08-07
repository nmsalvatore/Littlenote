"Functional tests for a curious user."

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

    def test_user_story(self):
        # George (because curious, of course) decides to check out the
        # Littlenote website to see what all the fuss is about.
        self.browser.get(self.live_server_url)

        # He checks the title of the page to make sure it looks like
        # what he's looking for.
        self.assertIn("littlenote", self.browser.title.lower())

        # He sees a form where he can provide his email to presumably
        # sign up or log in.
        continue_with_email_button = self.browser.find_element(By.ID, "continue_with_email_button")
        self.assertIn("continue", continue_with_email_button.text.lower())

        # Being the curious boy George is, he looks around to see if
        # he can get some more information before he commits to anything.
        nav_links = self.browser.find_elements(By.CSS_SELECTOR, "nav > menu a")
        nav_texts = [link.text.lower() for link in nav_links]
        self.assertIn("what is littlenote?", nav_texts)

        # Look at that! What is this? Exactly what George was thinking.
        # He clicks on the link and is navigated to a section
        # that explains what Littlenote is all about.
        what_link = self.browser.find_element(By.XPATH, "//a[contains(text(),'What is Littlenote?')]")
        what_link.click()

        self.fail("Finish George's journey!")
