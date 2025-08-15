import re

from django.core import mail
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class UserInteractions:
    """
    Extension of LiveServerTestCase to include live user interactions
    for the Littlenote UI.
    """

    def __init__(self, browser):
        self.browser = browser
        self.wait = WebDriverWait(self.browser, timeout=5)

    def login_returning_user(self, email):
        """
        Full login of returning user.
        """
        self.enter_email_address(email)
        self.click_continue_with_email_button()
        passcode = self.copy_passcode_from_email()
        self.enter_passcode(passcode)
        self.click_login_button()

    def signup_and_login_new_user(self, email):
        """
        Full signup and login of new user.
        """
        self.enter_email_address(email)
        self.click_continue_with_email_button()
        passcode = self.copy_passcode_from_email()
        self.enter_passcode(passcode)
        self.click_signup_button()

    def enter_email_address(self, email_address):
        """
        User enters their email address into the form.
        """
        email_input = self.browser.find_element(By.ID, "continue_with_email_input")
        email_input.send_keys(email_address)

    def click_continue_with_email_button(self):
        """
        User click of the "Continue with email" button.
        """
        email_button = self.browser.find_element(By.ID, "continue_with_email_button")
        email_button.click()

    def copy_passcode_from_email(self):
        """
        User copies passcode from email.
        """
        email_message = mail.outbox[0]
        passcode_match = re.search(r"Your one-time passcode is (\d{6})", email_message.subject)
        return passcode_match.group(1)

    def enter_passcode(self, passcode):
        """
        User enters the passcode into the form.
        """
        passcode_input = self.wait.until(EC.presence_of_element_located((By.NAME, "passcode")))
        passcode_input.send_keys(passcode)

    def click_login_button(self):
        """
        User clicks the login button.
        """
        login_button = self.browser.find_element(By.ID, "login_button")
        login_button.click()

    def click_signup_button(self):
        """
        User clicks the sign-up button.
        """
        signup_button = self.browser.find_element(By.ID, "signup_button")
        signup_button.click()
