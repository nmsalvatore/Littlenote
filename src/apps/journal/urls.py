from django.urls import path

from .views import home

app_name = "journal"

urlpatterns = [
    path("", home, name="home")
]
