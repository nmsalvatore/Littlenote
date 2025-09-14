from django.urls import path

from .views import JournalEntryCreateView, home

app_name = "journal"

urlpatterns = [
    path("", home, name="home"),
    path("new-entry/", JournalEntryCreateView.as_view(), name="new-entry")
]
