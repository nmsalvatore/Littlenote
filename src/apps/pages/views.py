import time

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .utils import auth_utils


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
            return auth_utils.render_email_form(request)

        # Logic for email submission.
        elif user_email and not user_passcode:
            # Set the response context for the passcode form, including
            # whether the user already has an account or not.
            context = {"email": user_email}
            user = User.objects.filter(email=user_email)
            context["user_has_account"] = user.exists()

            # Generate a new passcode.
            passcode = auth_utils.generate_passcode()

            # Set the passcode, user email, and passcode expiration
            # time in a session.
            auth_utils.set_passcode_session(request, user_email, passcode)

            # Email the passcode to the user.
            auth_utils.send_passcode_email(user_email, passcode)

            return auth_utils.render_passcode_form(request, context)

        # Logic for passcode submission.
        if user_email and user_passcode:
            # Get the passcode session data.
            passcode_data = request.session.get("passcode")

            # Expired session validation. Form should revert to email
            # form since success is now impossible.
            if not passcode_data:
                messages.error(request, "Session has expired. Please try again.")
                return auth_utils.render_email_form(request)

            # Invalid session data validation. Form should revert to
            # email form since funny business indicated.
            saved_passcode = passcode_data.get("code")
            saved_email = passcode_data.get("email")
            passcode_expiration = passcode_data.get("expires_at")
            if not all([saved_passcode, saved_email, passcode_expiration]):
                messages.error(request, "Invalid session data. Please try again.")
                return auth_utils.render_email_form(request)

            # Invalid email validation. Form should revert to email
            # form since funny business indicated.
            elif saved_email != user_email:
                messages.error(request, "Invalid email address. Please try again.")
                auth_utils.delete_passcode_session_data(request)
                return auth_utils.render_email_form(request)

            # Incorrect passcode validation. User should remain on the
            # passcode form in case something was entered incorrectly.
            elif saved_passcode != user_passcode:
                messages.error(request, "Incorrect passcode. Please check your email.")
                context = {"email": user_email}
                return auth_utils.render_passcode_form(request, context)

            # Expired passcode validation. Form should revert to email
            # form since success is now impossible.
            passcode_expired = time.perf_counter() > passcode_expiration
            if passcode_expired:
                messages.error(request, "Passcode has expired. Please try again.")
                auth_utils.delete_passcode_session_data(request)
                return auth_utils.render_email_form(request)

            # Passcode success path.
            elif user_passcode == saved_passcode:
                # Get the existing user or create a new user if a user
                # with the provided email doesn't exist.
                user, user_is_new = User.objects.get_or_create(
                    email=user_email, defaults={"username": user_email}
                )

                login(request, user)
                auth_utils.delete_passcode_session_data(request)

                if user_is_new:
                    messages.success(request, "Welcome to Littlenote!")

                return redirect("pages:dashboard")


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"
