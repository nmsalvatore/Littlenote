from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from src.apps.journal.models import JournalEntry


class JournalEntryCreateView(LoginRequiredMixin, CreateView):
    """
    View for journal entry creation.
    """
    model = JournalEntry
    fields = ["content"]
    success_url = reverse_lazy("journal:home")
    redirect_field_name = None

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class JournalEntryListView(LoginRequiredMixin, ListView):
    """
    View for journal entry list.
    """
    model = JournalEntry
    template_name = "journal/journal.html"
    context_object_name = "journal_entries"
    redirect_field_name = None

    def get_queryset(self):
        user = get_user(self.request)
        return JournalEntry.objects.filter(author=user)
