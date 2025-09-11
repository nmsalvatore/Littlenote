from django.conf import settings
from django.db import models
from django.db.models.fields import uuid
from django.utils import timezone


def generate_timestamp():
    """
    Generate timestamp for the note timestamp_id field.
    """
    return timezone.now().strftime("%Y%m%d%H%M%S")


class Note(models.Model):
    """
    Model for notes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp_id = models.CharField(max_length=14, default=generate_timestamp)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.title
