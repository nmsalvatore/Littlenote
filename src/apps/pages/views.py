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
        user_email = request.POST.get("email")
        user_passcode = request.POST.get("passcode")

        if not user_email or "@" not in user_email:
            messages.error(request, "Invalid email address. Please try again.")
            return render_email_form(request)

        if user_email and not user_passcode:
            context = {"email": user_email}
            user = User.objects.filter(email=user_email)
            context["user_has_account"] = user.exists()
            send_passcode(request, user_email)
            return render_passcode_form(request, context)

        if user_email and user_passcode:
            passcode_data = request.session.get("passcode")

            if not passcode_data:
                messages.error(request, "Session has expired. Please try again.")
                return render_email_form(request)

            saved_passcode = passcode_data.get("code")
            saved_email = passcode_data.get("email")
            passcode_expiration = passcode_data.get("expires_at")

            del request.session["passcode"]

            if not all([saved_passcode, saved_email, passcode_expiration]):
                messages.error(request, "Invalid session data. Please try again.")
                return render_email_form(request)

            if saved_email != user_email:
                messages.error(request, "Invalid email address. Please try again.")
                return render_email_form(request)

            if saved_passcode != user_passcode:
                messages.error(request, "Incorrect passcode. Please check your email.")
                context = {"email": user_email}
                return render_passcode_form(request)

            passcode_expired = time.perf_counter() > passcode_expiration

            if passcode_expired:
                messages.error(request, "Passcode has expired. Please try again.")
                return render_email_form(request)

            if user_passcode == saved_passcode and not passcode_expired:
                user, user_is_new = User.objects.get_or_create(
                    email=user_email,
                    defaults={"username": user_email}
                )

                login(request, user)

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


def send_passcode(request, email):
    """
    Generate and send the passcode to the user, saving the passcode
    data in a session.
    """
    passcode = generate_passcode()
    set_session_passcode(request, email, passcode)
    send_passcode_email(email, passcode)


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

def set_session_passcode(request, email, code):
    """
    Set the session passcode value as a dictionary containing the
    user email, passcode, and expiration time.
    """
    request.session["passcode"] = {
        "code": code,
        "email": email,
        "expires_at": time.perf_counter() + 180,
    }


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"
