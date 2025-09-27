"""Authentication utilities for passwordless login."""

import secrets
import time

from django.conf import settings
from django.core.mail import send_mail
import resend

from ..constants import AuthSessionKeys, EmailTemplates, ErrorMessages, AuthConfig


def normalize_email(email):
    """
    Normalize email address by setting to lowercase and removing
    whitespace.
    """
    return email.lower().strip()

def generate_passcode():
    """
    Generate a random 6-digit passcode.
    """
    return f"{secrets.randbelow(900000) + AuthConfig.PASSCODE_MIN_VALUE}"

def send_passcode_email(email, passcode):
    """
    Send email containing the one-time passcode for login.
    """
    subject = EmailTemplates.SUBJECT.format(passcode=passcode)
    message = EmailTemplates.EMAIL.format(passcode=passcode)

    if hasattr(settings, 'RESEND_API_KEY') and getattr(settings, 'RESEND_API_KEY'):
        try:
            resend.api_key = settings.RESEND_API_KEY
            resend.Emails.send({
                "from": settings.SERVER_EMAIL,
                "to": [email],
                "subject": subject,
                "text": message,
            })
        except Exception:
            # Fallback to SMTP if Resend fails
            send_mail(subject, message, settings.SERVER_EMAIL, [email], fail_silently=False)
    else:
        # Use SMTP for development/local
        send_mail(subject, message, settings.SERVER_EMAIL, [email], fail_silently=False)

def set_passcode_session(request, email, code):
    """
    Set the passcode session data.
    """
    request.session[AuthSessionKeys.PASSCODE] = {
        AuthSessionKeys.PASSCODE_CODE: code,
        AuthSessionKeys.PASSCODE_EMAIL: email,
        AuthSessionKeys.PASSCODE_EXPIRATION: time.perf_counter() + AuthConfig.PASSCODE_LIFETIME
    }

def delete_passcode_session_data(request):
    """
    Delete the passcode session data if it exists.
    """
    if request.session.get(AuthSessionKeys.PASSCODE):
        del request.session[AuthSessionKeys.PASSCODE]

def validate_passcode_session(request, user_email, user_passcode):
    """
    Validation on passcode session data.
    """
    passcode_data = request.session.get(AuthSessionKeys.PASSCODE)

    if not passcode_data:
        return False, ErrorMessages.EXPIRED_SESSION, True

    # Handle cases where session data might be corrupted or wrong type
    if not isinstance(passcode_data, dict):
        return False, ErrorMessages.INVALID_SESSION, True

    saved_passcode = passcode_data.get(AuthSessionKeys.PASSCODE_CODE)
    saved_email = passcode_data.get(AuthSessionKeys.PASSCODE_EMAIL)
    passcode_expiration = passcode_data.get(AuthSessionKeys.PASSCODE_EXPIRATION)

    if not all([saved_passcode, saved_email, passcode_expiration]):
        return False, ErrorMessages.INVALID_SESSION, True

    if saved_email != user_email:
        return False, ErrorMessages.INCORRECT_EMAIL, True

    if saved_passcode != user_passcode:
        return False, ErrorMessages.INCORRECT_PASSCODE, False

    if time.perf_counter() >= passcode_expiration:
        return False, ErrorMessages.EXPIRED_PASSCODE, True

    return True, None, False
