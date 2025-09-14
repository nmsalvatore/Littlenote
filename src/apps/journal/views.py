from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from src.apps.journal.models import JournalEntry


def home(request):
    return render(request, "journal/journal.html")


class JournalEntryCreateView(CreateView):
    """
    View for journal entry creation.
    """
    model = JournalEntry
    fields = ["content"]
    success_url = reverse_lazy("journal:home")
