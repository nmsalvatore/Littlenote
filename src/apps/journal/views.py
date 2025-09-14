from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from src.apps.journal.models import JournalEntry


class JournalEntryCreateView(CreateView):
    """
    View for journal entry creation.
    """
    model = JournalEntry
    fields = ["content"]
    success_url = reverse_lazy("journal:home")


class JournalEntryListView(ListView):
    """
    View for journal entry list.
    """
    model = JournalEntry
    template_name = "journal/journal.html"
    context_object_name = "journal_entries"
