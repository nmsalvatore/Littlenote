"""Integration tests for auth flows."""

import time

from django.contrib.auth import get_user, get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from src.apps.pages.constants import AuthSessionKeys, ErrorMessages, SuccessMessages


User = get_user_model()


class AuthTestCase(TestCase):
    """Base test case with helper methods for auth flow testing."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.front_page_url = reverse("pages:front")

    def setUp(self):
        super().setUp()
        # Use client without CSRF checks for auth flow testing
        from django.test.client import Client
        self.client = Client(enforce_csrf_checks=False)

    def _submit_email(self, email):
        """Submit the user email to the form."""
        return self.client.post(self.front_page_url, {"email": email})

    def _get_correct_passcode(self):
        """Get the correct passcode from the session data."""
        passcode_data = self.client.session[AuthSessionKeys.PASSCODE]
        return passcode_data[AuthSessionKeys.PASSCODE_CODE]

    def _generate_incorrect_passcode(self):
        """Generate an incorrect passcode by flipping the last digit."""
        passcode = self._get_correct_passcode()
        return passcode[:-1] + ("0" if passcode[-1] != "0" else "1")

    def _submit_passcode(self, email, passcode):
        """Submit the passcode to the form."""
        return self.client.post(self.front_page_url, {"email": email, "passcode": passcode})

    def _expire_passcode(self):
        """Force passcode expiration by setting expiration time in the past."""
        passcode_data = self.client.session[AuthSessionKeys.PASSCODE]
        passcode_data[AuthSessionKeys.PASSCODE_EXPIRATION] = time.perf_counter() - 10

        session = self.client.session
        session[AuthSessionKeys.PASSCODE] = passcode_data
        session.save()

    def _expire_session(self):
        """Force session to expire by deleting the passcode key."""
        session = self.client.session
        del session[AuthSessionKeys.PASSCODE]
        session.save()


@override_settings(RATELIMIT_ENABLE=False)
class AuthPasscodeTest(AuthTestCase):
    """
    Integration tests for passcode submission in auth flow.
    """

    def setUp(self):
        self.user_email = "testuser@example.com"
        self.imposter_email = "sketchyguy@example.com"

        # Submit email to navigate to the passcode form.
        self._submit_email(self.user_email)

    def test_correct_passcode_creates_new_user(self):
        """
        Test that submission of correct passcode creates a new user,
        if user doesn't already exist.
        """
        passcode = self._get_correct_passcode()
        self._submit_passcode(self.user_email, passcode)
        user = User.objects.filter(email=self.user_email)
        self.assertTrue(user.exists())

    def test_incorrect_passcode_does_not_create_new_user(self):
        """
        Test that submission of incorrect passcode does not create a
        new user.
        """
        passcode = self._generate_incorrect_passcode()
        self._submit_passcode(self.user_email, passcode)
        user = User.objects.filter(email=self.user_email)
        self.assertFalse(user.exists())

    def test_incorrect_passcode_shows_error_message(self):
        """
        Test that submitting an incorrect passcode keeps the user on the
        same page and shows the relevant error message.
        """
        passcode = self._generate_incorrect_passcode()
        response = self._submit_passcode(self.user_email, passcode)
        self.assertContains(response, ErrorMessages.INCORRECT_PASSCODE)

    def test_incorrect_passcode_does_not_authenticate(self):
        """
        Test that submitting an incorrect passcode doesn't authenticate
        the user.
        """
        passcode = self._generate_incorrect_passcode()
        self._submit_passcode(self.user_email, passcode)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_incorrect_passcode_doesnt_clear_email_input_value(self):
        """
        Test that submitting an incorrect passcode doesn't clear the email
        from the email input form.
        """
        passcode = self._generate_incorrect_passcode()
        response = self._submit_passcode(self.user_email, passcode)
        self.assertContains(response, self.user_email)

    def test_incorrect_passcode_doesnt_clear_session(self):
        """
        Test that submitting an incorrect passcode doesn't clear the
        session data containing the passcode.
        """
        passcode = self._generate_incorrect_passcode()
        self._submit_passcode(self.user_email, passcode)
        self.assertNotEqual(self.client.session.get(AuthSessionKeys.PASSCODE), None)

    def test_correct_passcode_after_incorrect_passcode(self):
        """
        Test that user can successfully authenticate with the correct
        passcode after submitting an incorrect passcode.
        """
        incorrect_passcode = self._generate_incorrect_passcode()
        correct_passcode = self._get_correct_passcode()
        self._submit_passcode(self.user_email, incorrect_passcode)
        self._submit_passcode(self.user_email, correct_passcode)
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_expired_passcode_shows_error_message(self):
        """
        Test that submission of an expired passcode keeps the user on
        the same page and shows the relevant error message.
        """
        self._expire_passcode()
        passcode = self._get_correct_passcode()
        response = self._submit_passcode(self.user_email, passcode)
        self.assertContains(response, ErrorMessages.EXPIRED_PASSCODE)

    def test_expired_passcode_does_not_authenticate(self):
        """
        Test that submission of a correct passcode after it has expired
        does not authenticate the user.
        """
        self._expire_passcode()
        passcode = self._get_correct_passcode()
        self._submit_passcode(self.user_email, passcode)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_expired_passcode_clears_session(self):
        """
        Test that submission of an expired passcode clears the session
        data containing the passcode.
        """
        self._expire_passcode()
        passcode = self._get_correct_passcode()
        self._submit_passcode(self.user_email, passcode)
        self.assertEqual(self.client.session.get(AuthSessionKeys.PASSCODE), None)

    def test_expired_session_shows_error_message(self):
        """
        Test that submission of passcode after the session has expired
        keeps the user on the same page and shows the relevant error
        message.
        """
        passcode = self._get_correct_passcode()
        self._expire_session()
        response = self._submit_passcode(self.user_email, passcode)
        self.assertContains(response, ErrorMessages.EXPIRED_SESSION)

    def test_expired_session_does_not_authenticate(self):
        """
        Test that submission of passcode after the session has expired
        does not authenticate the user.
        """
        passcode = self._get_correct_passcode()
        self._expire_session()
        self._submit_passcode(self.user_email, passcode)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_expired_session_clears_session(self):
        """
        Test that submission of passcode after the session has expired
        clears the session data containing the passcode.
        """
        passcode = self._get_correct_passcode()
        self._expire_session()
        self._submit_passcode(self.user_email, passcode)
        self.assertEqual(self.client.session.get(AuthSessionKeys.PASSCODE), None)

    def test_incorrect_email_in_passcode_submission_shows_error_message(self):
        """
        Test that passcode submission with an incorrect email address
        keeps the user on the same page and shows an error message.
        """
        passcode = self._get_correct_passcode()
        response = self._submit_passcode(self.imposter_email, passcode)
        self.assertContains(response, ErrorMessages.INCORRECT_EMAIL)

    def test_incorrect_email_in_passcode_submission_does_not_authenticate_user(self):
        """
        Test that passcode submission with an incorrect email address
        does not authenticate the user.
        """
        passcode = self._get_correct_passcode()
        self._submit_passcode(self.imposter_email, passcode)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_incorrect_email_in_passcode_submission_clears_session(self):
        """
        Test that passcode submission with an incorrect email address
        clears the session data containing the passcode.
        """
        passcode = self._get_correct_passcode()
        self._submit_passcode(self.imposter_email, passcode)
        self.assertEqual(self.client.session.get(AuthSessionKeys.PASSCODE), None)


@override_settings(RATELIMIT_ENABLE=False)
class AuthEmailTest(AuthTestCase):
    """
    Integration tests for email submission in auth flow.
    """

    def setUp(self):
        self.EMAIL_INPUT_ID = "continue_with_email_input"
        self.PASSCODE_INPUT_ID = "passcode_input"

        self.valid_user_email = "testuser@example.com"
        self.invalid_user_email = "testuser"

    def test_valid_email_renders_passcode_form(self):
        """
        Test that submission of valid email address renders the
        passcode form.
        """
        response = self._submit_email(self.valid_user_email)
        self.assertContains(response, self.PASSCODE_INPUT_ID)

    def test_valid_email_does_not_create_user(self):
        """
        Test that submission of valid email address does not create a
        new user.
        """
        self._submit_email(self.valid_user_email)
        user = User.objects.filter(email=self.valid_user_email)
        self.assertFalse(user.exists())

    def test_invalid_email_shows_error_message(self):
        """
        Test that submission of invalid email address keeps the user
        on the same page and shows an error message.
        """
        response = self._submit_email(self.invalid_user_email)
        self.assertContains(response, ErrorMessages.INVALID_EMAIL)

    def test_invalid_email_does_not_render_passcode_form(self):
        """
        Test that submission of invalid email address keeps the user
        on the email form and does not show passcode input.
        """
        response = self._submit_email(self.invalid_user_email)
        self.assertContains(response, self.EMAIL_INPUT_ID)
        self.assertNotContains(response, self.PASSCODE_INPUT_ID)
