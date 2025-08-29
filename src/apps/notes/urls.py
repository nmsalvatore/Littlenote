from django.urls import path

from .views import AllNotesView, NewNoteView, NoteDetailView

app_name = "notes"

urlpatterns = [
    path("", AllNotesView.as_view(), name="all"),
    path("note/<int:pk>/", NoteDetailView.as_view(), name="detail"),
    path("new/", NewNoteView.as_view(), name="new")
]
