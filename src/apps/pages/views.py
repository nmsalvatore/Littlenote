"""Pages app views."""

import time

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from .utils import auth_utils


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
            return self._render_email_form(request)

        elif user_email and not user_passcode:
            return self._handle_email_submission(request, user_email)

        if user_email and user_passcode:
            return self._handle_passcode_submission(request, user_email, user_passcode)


    def _handle_email_submission(self, request, user_email):
        """
        Handle email submission and send passcode to user.
        """
        context = {"email": user_email}
        user = User.objects.filter(email=user_email)
        context["user_has_account"] = user.exists()

        passcode = auth_utils.generate_passcode()
        auth_utils.set_passcode_session(request, user_email, passcode)
        auth_utils.send_passcode_email(user_email, passcode)

        return self._render_passcode_form(request, context)

    def _handle_passcode_submission(self, request, user_email, user_passcode):
        """
        Handle passcode submission and authentication.
        """
        is_valid, message, should_reset = (
            auth_utils.validate_passcode_session(request, user_email, user_passcode)
        )

        if not is_valid:
            messages.error(request, message)
            return self._handle_form_reset(request, should_reset, user_email)

        user, user_is_new = User.objects.get_or_create(
            email=user_email, defaults={"username": user_email}
        )

        login(request, user)
        auth_utils.delete_passcode_session_data(request)
        self._welcome_new_user(request, user_is_new)

        return redirect("pages:dashboard")

    def _welcome_new_user(self, request, user_is_new):
        """
        Welcome new users with a little welcome message.
        """
        if user_is_new:
            messages.success(request, "Welcome to Littlenote!")

    def _handle_form_reset(self, request, should_reset, user_email):
        """
        Handle form reset when passcode session data is invalid.
        """
        if should_reset:
            auth_utils.delete_passcode_session_data(request)
            return self._render_email_form(request)
        else:
            # Clear the passcode form.
            context = {"email": user_email}
            return self._render_passcode_form(request, context)

    def _render_email_form(self, request, context={}):
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


    def _render_passcode_form(self, request, context={}):
        """
        Handle passcode form render based on whether the request
        includes an HX-Request header.
        """
        if request.headers.get("HX-Request"):
            template_name = "partials/passcode_form.html"
        else:
            template_name = "front.html"

        context["passcode_sent"] = True
        return render(request, template_name, context)


class DashboardView(TemplateView):
    template_name = "pages/dashboard.html"
