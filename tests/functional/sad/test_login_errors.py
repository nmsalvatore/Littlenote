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
        response = self.client.post(self.front_page_url, {
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

        # User should see error message.
        self.assertContains(response, "Incorrect passcode")

        # User email should still be in email input.
        self.assertContains(response, self.user_email)

        # User should still be on same page.
        self.assertEqual(response.status_code, 200)

        # User should not be logged in.
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # Session data should persist.
        self.assertNotEqual(self.client.session.get("passcode"), None)

    def test_correct_passcode_after_wrong_passcode(self):
        # Submit user email address.
        response = self.client.post(self.front_page_url, {
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

        # User should not be logged in.
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # Submit the correct passcode.
        response = self.client.post(self.front_page_url, {
            "email": self.user_email,
            "passcode": correct_passcode,
        }, follow=True)

        # User should not be logged in.
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

        # User should see welcome message.
        self.assertContains(response, "Welcome to Littlenote!")

        # Session data should be removed.
        self.assertEqual(self.client.session.get("passcode"), None)

    def test_expired_passcode(self):
        # Submit user email address.
        response = self.client.post(self.front_page_url, {
            "email": self.user_email
        })

        # Manually expire the passcode
        passcode_data = self.client.session["passcode"]
        passcode_data["expires_at"] = time.perf_counter() - 10

        # Save session data
        session = self.client.session
        session["passcode"] = passcode_data
        session.save()

        # Get the correct passcode
        correct_passcode = passcode_data.get("code")

        # Submit the correct passcode.
        response = self.client.post(self.front_page_url, {
            "email": self.user_email,
            "passcode": correct_passcode
        })

        # User should see error message.
        self.assertContains(response, "Passcode has expired")

        # User should still be on same page.
        self.assertEqual(response.status_code, 200)

        # User should not be logged in.
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # Session data should be removed.
        self.assertEqual(self.client.session.get("passcode"), None)

    def test_expired_session(self):
        # Submit user email address.
        response = self.client.post(self.front_page_url, {
            "email": self.user_email
        })

        # Get the correct passcode.
        passcode_data = self.client.session["passcode"]
        correct_passcode = passcode_data.get("code")

        # Manually expire the session data and save.
        session = self.client.session
        del session["passcode"]
        session.save()

        # Submit the correct passcode.
        response = self.client.post(self.front_page_url, {
            "email": self.user_email,
            "passcode": correct_passcode
        })

        # User should see error message.
        self.assertContains(response, "Session has expired")

        # User should still be on same page.
        self.assertEqual(response.status_code, 200)

        # User should not be logged in.
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # Session data should be removed.
        self.assertEqual(self.client.session.get("passcode"), None)

    def test_wrong_email(self):
        # Submit user email address.
        response = self.client.post(self.front_page_url, {
            "email": self.user_email
        })

        # Get the correct passcode.
        passcode_data = self.client.session["passcode"]
        correct_passcode = passcode_data.get("code")

        # Submit the correct passcode.
        response = self.client.post(self.front_page_url, {
            "email": "wronguser@example.com",
            "passcode": correct_passcode
        })

        # User should see error message.
        self.assertContains(response, "Invalid email address")

        # User should still be on same page.
        self.assertEqual(response.status_code, 200)

        # User should not be logged in.
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

        # Session data should be removed.
        self.assertEqual(self.client.session.get("passcode"), None)

    def _generate_wrong_passcode(self, passcode):
        """
        Generate a purposefully incorrect passcode by flipping the last
        digit of the correct passcode.
        """
        return passcode[:-1] + "0" if passcode[-1] != "0" else "1"
