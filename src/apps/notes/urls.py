from django.urls import path

from .views import NotesHomeView

app_name = "notes"

urlpatterns = [
    path("", NotesHomeView.as_view(), name="home"),
]
