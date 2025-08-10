"""Unit tests for auth utility functions."""

from unittest.mock import patch

from django.test import SimpleTestCase

from src.apps.pages.utils.auth_utils import generate_passcode


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
