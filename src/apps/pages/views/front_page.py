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

    @method_decorator(ratelimit(
        key="ip",
        rate=AuthConfig.GENERAL_RATE_LIMIT,
        method="POST",
        block=True
    ))
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests from the home page.
        """
        try:
            user_email = normalize_email(request.POST.get("email"))
            user_passcode = request.POST.get("passcode")

            try:
                validate_email(user_email)
            except ValidationError:
                messages.error(request, ErrorMessages.INVALID_EMAIL)
                return self._render_email_form(request)

            if user_email and not user_passcode:
                return self._handle_email_submission(request, user_email)

            elif user_email and user_passcode:
                return self._handle_passcode_submission(request, user_email, user_passcode)

        except Ratelimited:
            messages.error(request, ErrorMessages.TOO_MANY_LOGIN_ATTEMPTS)
            return self._render_email_form(request)


    @method_decorator(ratelimit(
        key="post:email",
        rate=AuthConfig.EMAIL_REQUEST_RATE_LIMIT,
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

            passcode = generate_passcode()
            set_passcode_session(request, user_email, passcode)
            send_passcode_email(user_email, passcode)

            return self._render_passcode_form(request, context)

        except Ratelimited:
            messages.error(request, ErrorMessages.TOO_MANY_EMAIL_REQUESTS)
            return self._render_email_form(request)


    @method_decorator(ratelimit(
        key="post:email",
        rate=AuthConfig.PASSCODE_ATTEMPT_RATE_LIMIT,
        method="POST",
        block=True
    ))
    def _handle_passcode_submission(self, request, user_email, user_passcode):
        """
        Handle passcode submission and authentication.
        """
        try:
            is_valid, message, should_reset = (
                validate_passcode_session(request, user_email, user_passcode)
            )

            if not is_valid:
                messages.error(request, message)
                return self._handle_form_reset(request, should_reset, user_email)

            user, user_is_new = User.objects.get_or_create(
                email=user_email, defaults={"username": user_email}
            )

            login(request, user)
            delete_passcode_session_data(request)
            self._welcome_new_user(request, user_is_new)

            if request.headers.get("HX-Request"):
                response = HttpResponse()
                response["HX-Redirect"] = reverse("notes:list")
                return response

            return redirect(reverse("notes:list"))

        except Ratelimited:
            messages.error(request, ErrorMessages.TOO_MANY_PASSCODE_ATTEMPTS)
            context = {"email": user_email}
            return self._render_passcode_form(request, context)

    def _welcome_new_user(self, request, user_is_new):
        """
        Welcome new users with a little welcome message.
        """
        if user_is_new:
            messages.success(request, SuccessMessages.WELCOME_NEW_USER)

    def _handle_form_reset(self, request, should_reset, user_email):
        """
        Handle form reset when passcode session data is invalid.
        """
        if should_reset:
            delete_passcode_session_data(request)
            return self._render_email_form(request)
        else:
            user = User.objects.filter(email=user_email)
            context = {"email": user_email, "user_has_account": user.exists()}
            return self._render_passcode_form(request, context)

    def _render_email_form(self, request, context={}):
        """
        Handle email form render based on whether the request includes
        an HX-Request header.
        """
        if request.headers.get("HX-Request"):
            template_name = TemplatePaths.EMAIL_FORM
        else:
            template_name = TemplatePaths.FRONT_PAGE

        context["passcode_sent"] = False
        return render(request, template_name, context)


    def _render_passcode_form(self, request, context={}):
        """
        Handle passcode form render based on whether the request
        includes an HX-Request header.
        """
        if request.headers.get("HX-Request"):
            template_name = TemplatePaths.PASSCODE_FORM
        else:
            template_name = TemplatePaths.FRONT_PAGE

        context["passcode_sent"] = True
        return render(request, template_name, context)
