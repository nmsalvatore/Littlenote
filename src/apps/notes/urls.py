from django.urls import path

from .views import NewNoteView, NotesHomeView

app_name = "notes"

urlpatterns = [
    path("", NotesHomeView.as_view(), name="home"),
    path("new/", NewNoteView.as_view(), name="new_note")
]
