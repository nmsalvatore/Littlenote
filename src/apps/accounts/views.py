from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


class SignOutView(LogoutView):
    """
    View to sign out user and redirect to login page.
    """
    next_page = reverse_lazy("pages:front")
