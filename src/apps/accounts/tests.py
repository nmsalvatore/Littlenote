"""Tests for accounts app."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class SignOutViewTest(TestCase):
    """Tests for the SignOutView."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com"
        )
        self.signout_url = reverse("accounts:logout")
        self.front_page_url = reverse("pages:front")

    def test_signout_redirects_to_front_page(self):
        """Test that signing out redirects to the front page."""
        # Login user first
        self.client.force_login(self.user)

        # Verify user is authenticated
        response = self.client.get("/notes/")
        self.assertEqual(response.status_code, 200)

        # Sign out
        response = self.client.post(self.signout_url)

        # Should redirect to front page
        self.assertRedirects(response, self.front_page_url)

    def test_signout_logs_out_user(self):
        """Test that signing out actually logs out the user."""
        # Login user first
        self.client.force_login(self.user)

        # Verify user can access authenticated pages
        response = self.client.get("/notes/")
        self.assertEqual(response.status_code, 200)

        # Sign out
        self.client.post(self.signout_url)

        # Verify user can no longer access authenticated pages
        response = self.client.get("/notes/")
        self.assertRedirects(response, "/")

    def test_signout_get_request_not_allowed(self):
        """Test that GET requests to logout are not allowed by default."""
        # Login user first
        self.client.force_login(self.user)

        # Try to sign out with GET - should return 405 Method Not Allowed
        response = self.client.get(self.signout_url)

        # Should return 405 (Method Not Allowed)
        self.assertEqual(response.status_code, 405)

    def test_signout_when_not_logged_in(self):
        """Test that signout works even when user is not logged in."""
        # Don't log in user

        # Try to sign out
        response = self.client.post(self.signout_url)

        # Should still redirect to front page
        self.assertRedirects(response, self.front_page_url)
