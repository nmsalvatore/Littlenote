from django.urls import path

from .views import NotesListView, NewNoteView, NoteDetailView

app_name = "notes"

urlpatterns = [
    path("", NotesListView.as_view(), name="list"),
    path("<uuid:pk>/", NoteDetailView.as_view(), name="detail"),
    path("new/", NewNoteView.as_view(), name="new")
]
