from django.contrib import admin
from django.urls import path, include

from src.apps.pages import views as pages_views

urlpatterns = [
    path("", pages_views.HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls"))
]
