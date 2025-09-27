"""Views for the front page."""

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from ..constants import AuthConfig, ErrorMessages, SuccessMessages, TemplatePaths
from ..utils.auth_utils import (
    delete_passcode_session_data,
    generate_passcode,
    normalize_email,
    set_passcode_session,
    send_passcode_email,
    validate_passcode_session
)


User = get_user_model()


class FrontPageView(TemplateView):
    template_name =  TemplatePaths.FRONT_PAGE

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("notes:list")
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(ratelimit(key="ip", rate=AuthConfig.GENERAL_RATE_LIMIT, method="POST", block=True))
    def post(self, request, *args, **kwargs):
        """Handle POST requests from the home page."""
        try:
            user_email = normalize_email(request.POST.get("email", ""))
            user_passcode = request.POST.get("passcode", "")

            try:
                validate_email(user_email)
            except ValidationError:
                messages.error(request, ErrorMessages.INVALID_EMAIL)
                return self._render_email_form(request)

            if user_passcode:
                return self._handle_passcode_submission(request, user_email, user_passcode)
            else:
                return self._handle_email_submission(request, user_email)

        except Ratelimited:
            messages.error(request, ErrorMessages.TOO_MANY_LOGIN_ATTEMPTS)
            return self._render_email_form(request)


    @method_decorator(ratelimit(key="post:email", rate=AuthConfig.EMAIL_REQUEST_RATE_LIMIT, method="POST", block=True))
    def _handle_email_submission(self, request, user_email):
        """Handle email submission and send passcode to user."""
        try:
            context = {
                "email": user_email,
                "user_has_account": User.objects.filter(email=user_email).exists()
            }

            passcode = generate_passcode()
            set_passcode_session(request, user_email, passcode)
            send_passcode_email(user_email, passcode)

            return self._render_passcode_form(request, context)

        except Ratelimited:
            messages.error(request, ErrorMessages.TOO_MANY_EMAIL_REQUESTS)
            return self._render_email_form(request)


    @method_decorator(ratelimit(key="post:email", rate=AuthConfig.PASSCODE_ATTEMPT_RATE_LIMIT, method="POST", block=True))
    def _handle_passcode_submission(self, request, user_email, user_passcode):
        """Handle passcode submission and authentication."""
        try:
            is_valid, message, should_reset = validate_passcode_session(request, user_email, user_passcode)

            if not is_valid:
                messages.error(request, message)
                return self._handle_form_reset(request, should_reset, user_email)

            user, user_is_new = User.objects.get_or_create(
                email=user_email, defaults={"username": user_email}
            )

            login(request, user)
            delete_passcode_session_data(request)

            if user_is_new:
                messages.success(request, SuccessMessages.WELCOME_NEW_USER)

            redirect_url = reverse("notes:list")
            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = redirect_url
                return response

            return redirect(redirect_url)

        except Ratelimited:
            messages.error(request, ErrorMessages.TOO_MANY_PASSCODE_ATTEMPTS)
            return self._render_passcode_form(request, {"email": user_email})

    def _handle_form_reset(self, request, should_reset, user_email):
        """Handle form reset when passcode session data is invalid."""
        if should_reset:
            delete_passcode_session_data(request)
            return self._render_email_form(request)

        context = {
            "email": user_email,
            "user_has_account": User.objects.filter(email=user_email).exists()
        }
        return self._render_passcode_form(request, context)

    def _render_email_form(self, request, context=None):
        """Render email form based on request type."""
        context = context or {}
        context["passcode_sent"] = False

        template_name = TemplatePaths.EMAIL_FORM if request.headers.get("HX-Request") else TemplatePaths.FRONT_PAGE
        return render(request, template_name, context)

    def _render_passcode_form(self, request, context=None):
        """Render passcode form based on request type."""
        context = context or {}
        context["passcode_sent"] = True

        template_name = TemplatePaths.PASSCODE_FORM if request.headers.get("HX-Request") else TemplatePaths.FRONT_PAGE
        return render(request, template_name, context)
