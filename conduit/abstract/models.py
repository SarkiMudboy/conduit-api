from django.db import models
import uuid
from django.utils import timezone

class TimestampUUIDMixin(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

