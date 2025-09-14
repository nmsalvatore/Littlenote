from django.contrib import admin

from src.apps.journal.models import JournalEntry

admin.site.register(JournalEntry)
