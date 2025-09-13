from django.urls import path

from .views import (
    NotesListView,
    NoteCreateView,
    NoteDeleteView,
    NoteDetailView,
    NoteEditView,
)

app_name = "notes"

urlpatterns = [
    path("", NotesListView.as_view(), name="list"),
    path("<uuid:pk>/", NoteDetailView.as_view(), name="detail"),
    path("new/", NoteCreateView.as_view(), name="new"),
    path("edit/<uuid:pk>/", NoteEditView.as_view(), name="edit"),
    path("delete/<uuid:pk>/", NoteDeleteView.as_view(), name="delete"),
]
