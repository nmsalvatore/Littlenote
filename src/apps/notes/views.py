from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.views.generic.edit import DeleteView

from .models import Note


class NotesListView(LoginRequiredMixin, ListView):
    """
    View for the notes list page.
    """
    model = Note
    context_object_name = "notes"
    template_name = "notes/list.html"
    paginate_by = 10
    redirect_field_name = None

    def get_queryset(self):
        user = get_user(self.request)
        return Note.objects.filter(author=user)


class NoteCreateView(LoginRequiredMixin, CreateView):
    """
    View for the new note page.
    """
    model = Note
    fields = ["title", "content"]
    template_name = "notes/new.html"
    success_url = reverse_lazy("notes:list")
    redirect_field_name = None

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for note deletion.
    """
    model = Note
    success_url = reverse_lazy("notes:list")
    template_name = "notes/delete.html"
    redirect_field_name = None

    def get_object(self, queryset=None):
        note = super().get_object(queryset)

        if get_user(self.request) != note.author:
            raise Http404

        return note


class NoteDetailView(LoginRequiredMixin, DetailView):
    """
    View for a single note.
    """
    model = Note
    template_name = "notes/detail.html"
    redirect_field_name = None

    def get_object(self, queryset=None):
        note = super().get_object(queryset)

        if get_user(self.request) != note.author:
            raise Http404

        return note


class NoteEditView(LoginRequiredMixin, UpdateView):
    """
    View for note edit page.
    """
    model = Note
    fields = ["title", "content"]
    template_name = "notes/edit.html"
    context_object_name = "note"
    redirect_field_name = None
    success_url = reverse_lazy("notes:list")

    def get_object(self, queryset=None):
        note = super().get_object(queryset)

        if get_user(self.request) != note.author:
            raise Http404

        return note
