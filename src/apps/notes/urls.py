from django.urls import path

from .views import AllNotesView, NewNoteView, NoteTagsView

app_name = "notes"

urlpatterns = [
    path("all/", AllNotesView.as_view(), name="all"),
    path("new/", NewNoteView.as_view(), name="new"),
    path("tags/", NoteTagsView.as_view(), name="tags")
]
