"""Unit tests for auth utility functions."""

import time
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.test.client import RequestFactory

from src.apps.pages.constants import AuthSessionKeys, ErrorMessages
from src.apps.pages.utils.auth_utils import (
    delete_passcode_session_data,
    generate_passcode,
    send_passcode_email,
    set_passcode_session,
    validate_passcode_session
)


class GeneratePasscodeTest(SimpleTestCase):
    """
    Unit tests for the generate_passcode function.
    """

    def test_returns_string(self):
        """
        Test that passcode is returned as a string.
        """
        passcode = generate_passcode()
        self.assertIsInstance(passcode, str)

    def test_length_is_six_digits(self):
        """
        Test that passcode is 8 characters long.
        """
        passcode = generate_passcode()
        self.assertEqual(len(passcode), 8)

    def test_contains_only_digits(self):
        """
        Test that passcode contains only digits.
        """
        passcode = generate_passcode()
        passcode_number = int(passcode)
        self.assertGreaterEqual(passcode_number, 10000000)
        self.assertLessEqual(passcode_number, 99999999)

    def test_no_leading_zeros(self):
        """
        Test that passcode contains no leading zeros.
        """
        passcode = generate_passcode()
        self.assertFalse(passcode.startswith("0"))

    def test_generates_different_codes(self):
        """
        Test the multiple calls generate different passcodes.
        """
        passcodes = [generate_passcode() for _ in range(100)]
        unique_passcodes = set(passcodes)
        self.assertEqual(len(passcodes), len(unique_passcodes))

    def test_distribution_across_range(self):
        """
        Test that passcodes are distributed across the valid range.
        """
        passcodes = [int(generate_passcode()) for _ in range(100)]

        low_range = [p for p in passcodes if 10000000 <= p < 40000000]
        mid_range = [p for p in passcodes if 40000000 <= p < 70000000]
        high_range = [p for p in passcodes if 70000000 <= p <= 99999999]

        ranges_hit = sum([len(low_range) > 0, len(mid_range) > 0, len(high_range) > 0])
        self.assertGreaterEqual(ranges_hit, 2, "Passcodes should be distributed across ranges")

    @patch("src.apps.pages.utils.auth_utils.secrets.randbelow")
    def test_uses_secrets_module(self, mock_randbelow):
        """
        Test that the function uses the secrets module for
        cryptographic randomness.
        """
        mock_randbelow.return_value = 12345678
        passcode = generate_passcode()
        mock_randbelow.assert_called_once_with(90000000)
        self.assertEqual(passcode, "22345678")

    @patch("src.apps.pages.utils.auth_utils.secrets.randbelow")
    def test_minimum_value_generation(self, mock_randbelow):
        """
        Test generation of minimum possible value.
        """
        mock_randbelow.return_value = 0
        passcode = generate_passcode()
        self.assertEqual(passcode, "10000000")

    @patch("src.apps.pages.utils.auth_utils.secrets.randbelow")
    def test_maximum_value_generation(self, mock_randbelow):
        """
        Test generation of maximum possible value.
        """
        mock_randbelow.return_value = 89999999
        passcode = generate_passcode()
        self.assertEqual(passcode, "99999999")

    def test_performance(self):
        """
        Test that generation is reasonably fast.
        """
        import time

        start_time = time.time()
        for _ in range(1000):
            generate_passcode()
        end_time = time.time()

        self.assertLess(end_time - start_time, 0.1)


class SendPasscodeEmailTest(SimpleTestCase):
    """
    Unit tests for send_passcode_email function.
    """
    @patch("src.apps.pages.utils.auth_utils.send_mail")
    def test_send_passcode_email_calls_send_mail_correctly(self, mock_send_mail):
        """
        Test that send_passcode_email calls send_mail with correct parameters.
        """
        email = "test@example.com"
        passcode = "12345678"

        send_passcode_email(email, passcode)

        mock_send_mail.assert_called_once_with(
            "Your one-time passcode is 12345678.",
            "Here is your one-time passcode for Littlenote: 12345678",
            settings.SERVER_EMAIL,
            ["test@example.com"],
            fail_silently=False
        )

    @patch("src.apps.pages.utils.auth_utils.send_mail")
    def test_send_passcode_email_handles_send_mail_exception(self, mock_send_mail):
        """
        Test that send_passcode_email propagates send_mail exceptions.
        """
        mock_send_mail.side_effect = Exception("SMTP Error")

        with self.assertRaises(Exception):
            send_passcode_email("test@example.com", "12345678")


class SessionManagementTest(TestCase):
    """
    Unit tests for session management functions.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = {}

    def test_set_passcode_session(self):
        """
        Test setting passcode session data.
        """
        email = "test@example.com"
        code = "12345678"

        set_passcode_session(self.request, email, code)

        passcode_data = self.request.session[AuthSessionKeys.PASSCODE]
        self.assertEqual(passcode_data["code"], code)
        self.assertEqual(passcode_data["email"], email)
        self.assertIn("expires_at", passcode_data)

    def test_delete_passcode_session_data_when_exists(self):
        """
        Test deleting existing passcode session data.
        """
        self.request.session[AuthSessionKeys.PASSCODE] = {"test": "data"}
        delete_passcode_session_data(self.request)
        self.assertNotIn(AuthSessionKeys.PASSCODE, self.request.session)

    def test_delete_passcode_session_data_when_not_exists(self):
        """
        Test deleting passcode session data when it doesn't exist.
        """
        delete_passcode_session_data(self.request)
        self.assertNotIn(AuthSessionKeys.PASSCODE, self.request.session)


class ValidatePasscodeSessionTest(TestCase):
    """
    Unit tests for edge cases in passcode validation.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = {}

    def test_validate_with_missing_fields(self):
        """
        Test validation with incomplete session data.
        """
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "email": "test@example.com",
            "expires_at": time.perf_counter() + 300
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, "test@example.com", "12345678"
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INVALID_SESSION)
        self.assertTrue(should_reset)

    def test_validate_with_none_values(self):
        """
        Test validation with None values in session data.
        """
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": None,
            "email": "test@example.com",
            "expires_at": time.perf_counter() + 300
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, "test@example.com", "12345678"
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INVALID_SESSION)
        self.assertTrue(should_reset)

    @patch("src.apps.pages.utils.auth_utils.time.perf_counter")
    def test_validate_timing_edge_case(self, mock_perf_counter):
        """
        Test validation at exact expiration boundary.
        """
        expiration_time = 1000
        mock_perf_counter.return_value = expiration_time

        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": "12345678",
            "email": "test@example.com",
            "expires_at": expiration_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, "test@example.com", "12345678"
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.EXPIRED_PASSCODE)
        self.assertTrue(should_reset)
