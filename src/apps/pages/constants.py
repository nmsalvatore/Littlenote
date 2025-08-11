"""Constants for the pages app."""


class AuthConfig:
    """
    Authentication-related constants.
    """
    # Passcode configuration
    PASSCODE_LENGTH = 8
    PASSCODE_LIFETIME = 300
    PASSCODE_MIN_VALUE = 10000000

    # Rate limits
    GENERAL_RATE_LIMIT = "15/m"
    EMAIL_REQUEST_RATE_LIMIT = "3/h"
    PASSCODE_ATTEMPT_RATE_LIMIT = "5/m"


class AuthSessionKeys:
    """
    Session key constants.
    """
    PASSCODE = "passcode"
    PASSCODE_CODE = "code"
    PASSCODE_EMAIL = "email"
    PASSCODE_EXPIRATION = "expires_at"


class EmailTemplates:
    """
    Email template constants.
    """
    SUBJECT = "Your one-time passcode is {passcode}."
    EMAIL = "Here is your one-time passcode for Littlenote: {passcode}"


class SuccessMessages:
    """
    User-facing success message constants.
    """
    WELCOME_NEW_USER = "Welcome to Littlenote!"


class ErrorMessages:
    """
    User-facing error message constants.
    """
    # Login errors
    EXPIRED_SESSION = "Session has expired. Please try again."
    INVALID_SESSION = "Invalid session data. Please try again."
    INVALID_EMAIL = "Invalid email address. Please try again."
    INCORRECT_EMAIL = "Incorrect email address. Please try again."
    INCORRECT_PASSCODE = "Incorrect passcode. Please try again."
    EXPIRED_PASSCODE = "Passcode has expired. Please try again."

    # Rate-limit errors
    TOO_MANY_LOGIN_ATTEMPTS = "Too many login attempts. Please wait a moment before trying again."
    TOO_MANY_EMAIL_REQUESTS = "Too many email requests. Please wait a moment before trying again."
    TOO_MANY_PASSCODE_ATTEMPTS = "Too many passcode attempts. Please wait a moment before trying again."


class TemplatePaths:
    """
    Template-related constants.
    """
    FRONT_PAGE = "pages/front.html"
    DASHBOARD = "dashboard/dashboard.html"

    # Partials
    EMAIL_FORM = "pages/partials/email_form.html"
    PASSCODE_FORM = "pages/partials/passcode_form.html"
