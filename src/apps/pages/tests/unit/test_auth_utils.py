"""Unit tests for auth utility functions."""

import time
from unittest.mock import Mock, patch, MagicMock

from django.conf import settings
from django.core.mail import send_mail
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.client import RequestFactory

from src.apps.pages.constants import AuthSessionKeys, ErrorMessages, AuthConfig
from src.apps.pages.utils.auth_utils import (
    delete_passcode_session_data,
    generate_passcode,
    normalize_email,
    send_passcode_email,
    set_passcode_session,
    validate_passcode_session
)


class NormalizeEmailTest(SimpleTestCase):
    """
    Unit tests for the normalize_email function.
    """
    def setUp(self):
        self.normalized_email = "testuser@example.com"

    def test_returns_lowercase(self):
        """
        Test that all-caps email is returned in lowercase.
        """
        email = normalize_email("TESTUSER@EXAMPLE.COM")
        self.assertEqual(email, self.normalized_email)

    def test_removes_whitespace(self):
        """
        Test that whitespace padded email is stripped of whitespace.
        """
        email = normalize_email("    testuser@example.com    ")
        self.assertEqual(email, self.normalized_email)

    def test_returns_lowercase_and_removes_whitespace(self):
        """
        Test that all-caps email also padded with whitespace is
        stripped of whitespace and returned in lowercase.
        """
        email = normalize_email("    TESTUSER@EXAMPLE.COM    ")
        self.assertEqual(email, self.normalized_email)


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
        Test that passcode is 6 characters long.
        """
        passcode = generate_passcode()
        self.assertEqual(len(passcode), 6)

    def test_contains_only_digits(self):
        """
        Test that passcode contains only digits.
        """
        passcode = generate_passcode()
        passcode_number = int(passcode)
        self.assertGreaterEqual(passcode_number, 100000)
        self.assertLessEqual(passcode_number, 999999)

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

        low_range = [p for p in passcodes if 100000 <= p < 400000]
        mid_range = [p for p in passcodes if 400000 <= p < 700000]
        high_range = [p for p in passcodes if 700000 <= p <= 999999]

        ranges_hit = sum([len(low_range) > 0, len(mid_range) > 0, len(high_range) > 0])
        self.assertGreaterEqual(ranges_hit, 2, "Passcodes should be distributed across ranges")

    @patch("src.apps.pages.utils.auth_utils.secrets.randbelow")
    def test_uses_secrets_module(self, mock_randbelow):
        """
        Test that the function uses the secrets module for
        cryptographic randomness.
        """
        mock_randbelow.return_value = 123456
        passcode = generate_passcode()
        mock_randbelow.assert_called_once_with(900000)
        self.assertEqual(passcode, "223456")

    @patch("src.apps.pages.utils.auth_utils.secrets.randbelow")
    def test_minimum_value_generation(self, mock_randbelow):
        """
        Test generation of minimum possible value.
        """
        mock_randbelow.return_value = 0
        passcode = generate_passcode()
        self.assertEqual(passcode, "100000")

    @patch("src.apps.pages.utils.auth_utils.secrets.randbelow")
    def test_maximum_value_generation(self, mock_randbelow):
        """
        Test generation of maximum possible value.
        """
        mock_randbelow.return_value = 899999
        passcode = generate_passcode()
        self.assertEqual(passcode, "999999")

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
    """Unit tests for send_passcode_email function."""

    def setUp(self):
        self.email = "test@example.com"
        self.passcode = "123456"
        self.subject = "Your one-time passcode is 123456."
        self.message = "Here is your one-time passcode for Littlenote: 123456"

    @override_settings(RESEND_API_KEY=None)
    @patch("src.apps.pages.utils.auth_utils.send_mail")
    def test_uses_smtp_when_no_resend_api_key(self, mock_send_mail):
        """Test SMTP is used when RESEND_API_KEY is not set."""
        send_passcode_email(self.email, self.passcode)

        mock_send_mail.assert_called_once_with(
            self.subject, self.message, settings.SERVER_EMAIL, [self.email], fail_silently=False
        )

    @override_settings(RESEND_API_KEY="")
    @patch("src.apps.pages.utils.auth_utils.send_mail")
    def test_uses_smtp_when_empty_resend_api_key(self, mock_send_mail):
        """Test SMTP is used when RESEND_API_KEY is empty."""
        send_passcode_email(self.email, self.passcode)

        mock_send_mail.assert_called_once_with(
            self.subject, self.message, settings.SERVER_EMAIL, [self.email], fail_silently=False
        )

    @override_settings(RESEND_API_KEY="test_api_key")
    @patch("src.apps.pages.utils.auth_utils.resend")
    def test_uses_resend_api_when_key_present(self, mock_resend):
        """Test Resend API is used when RESEND_API_KEY is set."""
        mock_resend.Emails.send.return_value = {"id": "email_id"}

        send_passcode_email(self.email, self.passcode)

        self.assertEqual(mock_resend.api_key, "test_api_key")
        mock_resend.Emails.send.assert_called_once_with({
            "from": settings.SERVER_EMAIL,
            "to": [self.email],
            "subject": self.subject,
            "text": self.message,
        })

    @override_settings(RESEND_API_KEY="test_api_key")
    @patch("src.apps.pages.utils.auth_utils.send_mail")
    @patch("src.apps.pages.utils.auth_utils.resend")
    def test_fallback_to_smtp_when_resend_fails(self, mock_resend, mock_send_mail):
        """Test fallback to SMTP when Resend API fails."""
        mock_resend.Emails.send.side_effect = Exception("API Error")

        send_passcode_email(self.email, self.passcode)

        mock_send_mail.assert_called_once_with(
            self.subject, self.message, settings.SERVER_EMAIL, [self.email], fail_silently=False
        )

    @override_settings(RESEND_API_KEY="test_api_key")
    @patch("src.apps.pages.utils.auth_utils.send_mail")
    @patch("src.apps.pages.utils.auth_utils.resend")
    def test_fallback_smtp_failure_propagates_exception(self, mock_resend, mock_send_mail):
        """Test that if both Resend and SMTP fail, exception is propagated."""
        mock_resend.Emails.send.side_effect = Exception("API Error")
        mock_send_mail.side_effect = Exception("SMTP Error")

        with self.assertRaises(Exception):
            send_passcode_email(self.email, self.passcode)

    @override_settings(RESEND_API_KEY=None)
    @patch("src.apps.pages.utils.auth_utils.send_mail")
    def test_smtp_failure_propagates_exception(self, mock_send_mail):
        """Test that SMTP failures are propagated."""
        mock_send_mail.side_effect = Exception("SMTP Error")

        with self.assertRaises(Exception):
            send_passcode_email(self.email, self.passcode)

    def test_email_content_formatting(self):
        """Test that email content is properly formatted with different passcodes."""
        test_cases = [
            ("123456", "Your one-time passcode is 123456.", "Here is your one-time passcode for Littlenote: 123456"),
            ("000000", "Your one-time passcode is 000000.", "Here is your one-time passcode for Littlenote: 000000"),
            ("999999", "Your one-time passcode is 999999.", "Here is your one-time passcode for Littlenote: 999999"),
        ]

        for passcode, expected_subject, expected_message in test_cases:
            with self.subTest(passcode=passcode):
                with patch("src.apps.pages.utils.auth_utils.send_mail") as mock_send_mail:
                    send_passcode_email(self.email, passcode)
                    mock_send_mail.assert_called_once_with(
                        expected_subject, expected_message, settings.SERVER_EMAIL, [self.email], fail_silently=False
                    )


class SessionManagementTest(TestCase):
    """Unit tests for session management functions."""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = {}
        self.email = "test@example.com"
        self.code = "123456"

    def test_set_passcode_session(self):
        """Test setting passcode session data."""
        set_passcode_session(self.request, self.email, self.code)

        passcode_data = self.request.session[AuthSessionKeys.PASSCODE]
        self.assertEqual(passcode_data["code"], self.code)
        self.assertEqual(passcode_data["email"], self.email)
        self.assertIn("expires_at", passcode_data)

        # Verify expiration is in the future
        self.assertGreater(passcode_data["expires_at"], time.perf_counter())
        # Verify expiration is approximately correct (within 5 seconds)
        expected_expiration = time.perf_counter() + AuthConfig.PASSCODE_LIFETIME
        self.assertAlmostEqual(passcode_data["expires_at"], expected_expiration, delta=5)

    def test_set_passcode_session_overwrites_existing(self):
        """Test that setting passcode session overwrites existing data."""
        # Set initial session data
        self.request.session[AuthSessionKeys.PASSCODE] = {"old": "data"}

        set_passcode_session(self.request, self.email, self.code)

        passcode_data = self.request.session[AuthSessionKeys.PASSCODE]
        self.assertEqual(passcode_data["code"], self.code)
        self.assertEqual(passcode_data["email"], self.email)
        self.assertNotIn("old", passcode_data)

    def test_delete_passcode_session_data_when_exists(self):
        """Test deleting existing passcode session data."""
        self.request.session[AuthSessionKeys.PASSCODE] = {"test": "data"}
        delete_passcode_session_data(self.request)
        self.assertNotIn(AuthSessionKeys.PASSCODE, self.request.session)

    def test_delete_passcode_session_data_when_not_exists(self):
        """Test deleting passcode session data when it doesn't exist."""
        delete_passcode_session_data(self.request)
        self.assertNotIn(AuthSessionKeys.PASSCODE, self.request.session)

    def test_delete_passcode_session_data_preserves_other_session_data(self):
        """Test that deleting passcode data doesn't affect other session data."""
        self.request.session["other_key"] = "other_value"
        self.request.session[AuthSessionKeys.PASSCODE] = {"test": "data"}

        delete_passcode_session_data(self.request)

        self.assertNotIn(AuthSessionKeys.PASSCODE, self.request.session)
        self.assertEqual(self.request.session["other_key"], "other_value")


class ValidatePasscodeSessionTest(TestCase):
    """Unit tests for passcode validation."""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = {}
        self.email = "test@example.com"
        self.passcode = "123456"
        self.future_time = time.perf_counter() + 300

    def test_validate_successful_case(self):
        """Test successful validation with correct data."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "email": self.email,
            "expires_at": self.future_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertTrue(is_valid)
        self.assertIsNone(message)
        self.assertFalse(should_reset)

    def test_validate_with_no_session_data(self):
        """Test validation when no session data exists."""
        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.EXPIRED_SESSION)
        self.assertTrue(should_reset)

    def test_validate_with_missing_code_field(self):
        """Test validation with missing code field."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "email": self.email,
            "expires_at": self.future_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INVALID_SESSION)
        self.assertTrue(should_reset)

    def test_validate_with_missing_email_field(self):
        """Test validation with missing email field."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "expires_at": self.future_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INVALID_SESSION)
        self.assertTrue(should_reset)

    def test_validate_with_missing_expires_at_field(self):
        """Test validation with missing expires_at field."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "email": self.email
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INVALID_SESSION)
        self.assertTrue(should_reset)

    def test_validate_with_none_values(self):
        """Test validation with None values in session data."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": None,
            "email": self.email,
            "expires_at": self.future_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INVALID_SESSION)
        self.assertTrue(should_reset)

    def test_validate_with_incorrect_email(self):
        """Test validation with incorrect email address."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "email": self.email,
            "expires_at": self.future_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, "wrong@example.com", self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INCORRECT_EMAIL)
        self.assertTrue(should_reset)

    def test_validate_with_incorrect_passcode(self):
        """Test validation with incorrect passcode."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "email": self.email,
            "expires_at": self.future_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, "wrong_code"
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INCORRECT_PASSCODE)
        self.assertFalse(should_reset)  # Don't reset session for incorrect passcode

    @patch("src.apps.pages.utils.auth_utils.time.perf_counter")
    def test_validate_with_expired_passcode(self, mock_perf_counter):
        """Test validation with expired passcode."""
        expiration_time = 1000
        mock_perf_counter.return_value = expiration_time + 1  # 1 second after expiration

        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "email": self.email,
            "expires_at": expiration_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.EXPIRED_PASSCODE)
        self.assertTrue(should_reset)

    @patch("src.apps.pages.utils.auth_utils.time.perf_counter")
    def test_validate_timing_edge_case_exactly_expired(self, mock_perf_counter):
        """Test validation at exact expiration boundary."""
        expiration_time = 1000
        mock_perf_counter.return_value = expiration_time  # Exactly at expiration

        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "email": self.email,
            "expires_at": expiration_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email, self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.EXPIRED_PASSCODE)
        self.assertTrue(should_reset)

    def test_validate_case_sensitivity(self):
        """Test that validation is case-sensitive for email."""
        self.request.session[AuthSessionKeys.PASSCODE] = {
            "code": self.passcode,
            "email": self.email.lower(),
            "expires_at": self.future_time
        }

        is_valid, message, should_reset = validate_passcode_session(
            self.request, self.email.upper(), self.passcode
        )

        self.assertFalse(is_valid)
        self.assertEqual(message, ErrorMessages.INCORRECT_EMAIL)
        self.assertTrue(should_reset)
