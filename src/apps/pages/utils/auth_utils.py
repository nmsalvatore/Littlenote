"""Authentication utilities for passwordless login."""

import secrets
import time

from django.conf import settings
from django.core.mail import send_mail


def generate_passcode():
    """
    Generate a random 8-digit passcode.
    """
    return f"{secrets.randbelow(90000000) + 10000000}"


def send_passcode_email(email, passcode):
    """
    Send email containing the one-time passcode for login.
    """
    send_mail(
        f"Your one-time passcode is {passcode}.",
        f"Here is your one-time passcode for Littlenote: {passcode}",
        settings.SERVER_EMAIL,
        [email],
        fail_silently=False
    )

def set_passcode_session(request, email, code):
    """
    Set the passcode session data.
    """
    PASSCODE_LIFE = 300  # 5 minutes

    request.session["passcode"] = {
        "code": code,
        "email": email,
        "expires_at": time.perf_counter() + PASSCODE_LIFE,
    }

def delete_passcode_session_data(request):
    """
    Delete the passcode session data if it exists.
    """
    if request.session.get("passcode"):
        del request.session["passcode"]

def validate_passcode_session(request, user_email, user_passcode):
    """
    Validation on passcode session data.
    """
    passcode_data = request.session.get("passcode")

    if not passcode_data:
        return False, "Session has expired. Please try again.", True

    saved_passcode = passcode_data.get("code")
    saved_email = passcode_data.get("email")
    passcode_expiration = passcode_data.get("expires_at")

    if not any([saved_passcode, saved_email, passcode_expiration]):
        return False, "Invalid session data. Please try again.", True

    if saved_email != user_email:
        return False, "Invalid email address. Please try again.", True

    if saved_passcode != user_passcode:
        return False, "Incorrect passcode. Please check your email.", False

    if time.perf_counter() > passcode_expiration:
        return False, "Passcode has expired. Please try again.", True

    return True, None, False
