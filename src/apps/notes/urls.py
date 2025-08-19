from django.urls import path

from .views import NewNoteView

app_name = "notes"

urlpatterns = [
    path("new/", NewNoteView.as_view(), name="new_note"),
]
