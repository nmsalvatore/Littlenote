import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.generic import TemplateView


User = get_user_model()


class FrontPageView(TemplateView):
    template_name = "front.html"

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests from the home page.
        """

        # Get email and passcode from form.
        user_email = request.POST.get("email")
        user_passcode = request.POST.get("passcode")

        # Email validation.
        if not user_email or "@" not in user_email:
            messages.error(request, "Invalid email address. Please try again.")
            return render_email_form(request)

        # Logic for email submission.
        elif user_email and not user_passcode:
            # Set the response context for the passcode form, including
            # whether the user already has an account or not.
            context = {"email": user_email}
            user = User.objects.filter(email=user_email)
            context["user_has_account"] = user.exists()

            # Generate a new passcode.
            passcode = generate_passcode()

            # Set the passcode, user email, and passcode expiration
            # time in a session.
            set_passcode_session(request, user_email, passcode)

            # Email the passcode to the user.
            send_passcode_email(user_email, passcode)

            return render_passcode_form(request, context)

        # Logic for passcode submission.
        if user_email and user_passcode:
            # Get the passcode session data.
            passcode_data = request.session.get("passcode")

            # Expired session validation. Form should revert to email
            # form since success is now impossible.
            if not passcode_data:
                messages.error(request, "Session has expired. Please try again.")
                return render_email_form(request)

            # Invalid session data validation. Form should revert to
            # email form since funny business indicated.
            saved_passcode = passcode_data.get("code")
            saved_email = passcode_data.get("email")
            passcode_expiration = passcode_data.get("expires_at")
            if not all([saved_passcode, saved_email, passcode_expiration]):
                messages.error(request, "Invalid session data. Please try again.")
                return render_email_form(request)

            # Invalid email validation. Form should revert to email
            # form since funny business indicated.
            elif saved_email != user_email:
                messages.error(request, "Invalid email address. Please try again.")
                delete_passcode_session_data(request)
                return render_email_form(request)

            # Incorrect passcode validation. User should remain on the
            # passcode form in case something was entered incorrectly.
            elif saved_passcode != user_passcode:
                messages.error(request, "Incorrect passcode. Please check your email.")
                context = {"email": user_email}
                return render_passcode_form(request, context)

            # Expired passcode validation. Form should revert to email
            # form since success is now impossible.
            passcode_expired = time.perf_counter() > passcode_expiration
            if passcode_expired:
                messages.error(request, "Passcode has expired. Please try again.")
                delete_passcode_session_data(request)
                return render_email_form(request)

            # Passcode success path.
            elif user_passcode == saved_passcode:
                # Get the existing user or create a new user if a user
                # with the provided email doesn't exist.
                user, user_is_new = User.objects.get_or_create(
                    email=user_email,
                    defaults={"username": user_email}
                )

                login(request, user)
                delete_passcode_session_data(request)

                if user_is_new:
                    messages.success(request, "Welcome to Littlenote!")

                return redirect("pages:dashboard")


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


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"
