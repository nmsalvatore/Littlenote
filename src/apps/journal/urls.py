from django.urls import path

from .views import JournalEntryCreateView, JournalEntryListView

app_name = "journal"

urlpatterns = [
    path("", JournalEntryListView.as_view(), name="home"),
    path("new-entry/", JournalEntryCreateView.as_view(), name="new-entry")
]
