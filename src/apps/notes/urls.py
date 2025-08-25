from django.urls import path

from .views import AllNotesView, NewNoteView

app_name = "notes"

urlpatterns = [
    path("", AllNotesView.as_view(), name="all"),
    path("new/", NewNoteView.as_view(), name="new")
]
