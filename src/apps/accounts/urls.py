from django.urls import path

from .views import SignOutView

app_name = "accounts"

urlpatterns = [
    path("logout/", SignOutView.as_view(), name="logout")
]
