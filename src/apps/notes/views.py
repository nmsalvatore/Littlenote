from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Note


class NotesListView(ListView):
    """
    View for the notes list page.
    """
    model = Note
    context_object_name = "notes"
    template_name = "notes/list.html"
    paginate_by = 25


class NewNoteView(CreateView):
    """
    View for the new note page.
    """
    model = Note
    fields = ["title", "content"]
    template_name = "notes/new.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NoteDetailView(DetailView):
    """
    View for a single note.
    """
    model = Note
    template_name = "notes/detail.html"
