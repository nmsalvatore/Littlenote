from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView


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

        days = []
        current_day = first_calendar_day

        while current_day <= last_calendar_day:
            days.append(current_day)
            current_day += timedelta(days=1)

        context["days"] = days
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


class NewNoteView(TemplateView):
    """
    View for the new note page.
    """
    template_name = "notes/new.html"


class NoteTagsView(TemplateView):
    """
    View for the note tags page.
    """
    template_name = "notes/tags.html"
