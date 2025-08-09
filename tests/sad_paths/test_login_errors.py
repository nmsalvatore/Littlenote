"""Test login errors."""

import time

from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.urls.base import reverse


User = get_user_model()


class FailedLoginTest(TestCase):
    """
    Testing suite for user login errors.
    """

    def setUp(self):
        self.user_email = "testuser@example.com"
        self.front_page_url = reverse("pages:front")

    def test_wrong_passcode(self):
        # Submit user email address.
        self.client.post(self.front_page_url, {
            "email": self.user_email
        })

        # Get the correct passcode.
        passcode_data = self.client.session["passcode"]
        correct_passcode = passcode_data["code"]

        # Submit the wrong passcode.
        wrong_passcode = self._generate_wrong_passcode(correct_passcode)
        response = self.client.post(self.front_page_url, {
            "email": self.user_email,
            "passcode": wrong_passcode
        })

        # User should see "Incorrect passcode" error message.
        self.assertContains(response, "Incorrect passcode")

        # User email should still be in email input.
        self.assertContains(response, self.user_email)

        # User should still be on same page.
        self.assertEqual(response.status_code, 200)

        # User should not be logged in.
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def _generate_wrong_passcode(self, passcode):
        """
        Generate a purposefully incorrect passcode by flipping the last
        digit of the correct passcode.
        """
        return passcode[:-1] + "0" if passcode[-1] != "0" else "1"
