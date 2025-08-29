from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView
from django.views.generic.base import TemplateView

from .models import Note


class AllNotesView(TemplateView):
    """
    View for the notes home page.
    """
    template_name = "notes/all.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        last_calendar_day = self._get_last_calendar_day()
        first_calendar_day = last_calendar_day - timedelta(days=363)

        note_counts = defaultdict(int)
        notes = Note.objects.filter(
            author=self.request.user,
            created_at__date__gte=first_calendar_day.date(),
            created_at__date__lte=last_calendar_day.date()
        )
        for note in notes:
            note_counts[note.created_at.date()] += 1

        days = []
        current_day = first_calendar_day
        while current_day <= last_calendar_day:
            count = note_counts[current_day.date()]

            if current_day > datetime.today():
                css_class = "null"
            elif count == 0:
                css_class = "level-0"
            elif count <= 1:
                css_class = "level-1"
            elif count <= 2:
                css_class = "level-2"
            else:
                css_class = "level-3"

            days.append({
                "date": current_day,
                "css_class": css_class,
                "count": count
            })
            current_day += timedelta(days=1)

        notes = Note.objects.filter(author=self.request.user)

        context["days"] = days
        context["notes"] = notes
        return context

    def _get_last_calendar_day(self):
        """
        Get the last calendar day for the heatmap. If today is
        Saturday, the last calendar day is today. Otherwise, the last
        calendar day is the next Saturday.
        """
        today = datetime.today()
        days_until_saturday = (5 - today.weekday()) % 7

        if days_until_saturday == 0:
            return today
        return today + timedelta(days=days_until_saturday)


class NewNoteView(CreateView):
    """
    View for the new note page.
    """
    model = Note
    fields = ["title", "content"]
    template_name = "notes/new.html"
    success_url = reverse_lazy("notes:all")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NoteDetailView(DetailView):
    """
    View for a single note.
    """
    model = Note
    template_name = "notes/detail.html"
