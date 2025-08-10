"""Pages app views."""

import time

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from .utils import auth_utils


User = get_user_model()


class FrontPageView(TemplateView):
    template_name = "front.html"

    @method_decorator(ratelimit(
        key="ip",
        rate="15/m",
        method="POST",
        block=True
    ))
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests from the home page.
        """
        try:
            user_email = request.POST.get("email")
            user_passcode = request.POST.get("passcode")

            try:
                validate_email(user_email)
            except ValidationError:
                messages.error(request, "Enter a valid email address.")
                return self._render_email_form(request)

            if user_email and not user_passcode:
                return self._handle_email_submission(request, user_email)

            elif user_email and user_passcode:
                return self._handle_passcode_submission(request, user_email, user_passcode)

        except Ratelimited:
            messages.error(request, "Too many login attempts. Please wait a moment before trying again.")
            return self._render_email_form(request)


    @method_decorator(ratelimit(
        key="post:email",
        rate="3/h",
        method="POST",
        block=True
    ))
    def _handle_email_submission(self, request, user_email):
        """
        Handle email submission and send passcode to user.
        """
        try:
            context = {"email": user_email}
            user = User.objects.filter(email=user_email)
            context["user_has_account"] = user.exists()

            passcode = auth_utils.generate_passcode()
            auth_utils.set_passcode_session(request, user_email, passcode)
            auth_utils.send_passcode_email(user_email, passcode)

            return self._render_passcode_form(request, context)

        except Ratelimited:
            messages.error(request, "Too many email submissions. Please wait a moment before trying again.")
            return self._render_email_form(request)


    @method_decorator(ratelimit(
        key="post:email",
        rate="5/m",
        method="POST",
        block=True
    ))
    def _handle_passcode_submission(self, request, user_email, user_passcode):
        """
        Handle passcode submission and authentication.
        """
        try:
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

        except Ratelimited:
            messages.error(request, "Too many passcode attempts. Please wait a moment before trying again.")
            context = {"email": user_email}
            return self._render_passcode_form(request, context)

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
