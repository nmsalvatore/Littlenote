"""Authentication utilities for passwordless login."""

import secrets
import time

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render


def generate_passcode():
    """
    Generate a random six-digit passcode.
    """
    return f"{secrets.randbelow(900000) + 100000}"


def render_email_form(request, context={}):
    """
    Handle email form render based on whether the request includes
    an HX-Request header.
    """
    if request.headers.get("HX-Request"):
        template_name = "partials/email_form.html"
    else:
        template_name = "front.html"

    context["passcode_sent"] = False
    return render(request, template_name, context)


def render_passcode_form(request, context={}):
    """
    Handle passcode form render based on whether the request includes
    an HX-Request header.
    """
    if request.headers.get("HX-Request"):
        template_name = "partials/passcode_form.html"
    else:
        template_name = "front.html"

    context["passcode_sent"] = True
    return render(request, template_name, context)


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
    request.session["passcode"] = {
        "code": code,
        "email": email,
        "expires_at": time.perf_counter() + 180,
    }

def delete_passcode_session_data(request):
    """
    Delete the passcode session data if it exists.
    """
    if request.session.get("passcode"):
        del request.session["passcode"]
