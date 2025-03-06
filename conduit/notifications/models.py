from abstract.models import TimestampUUIDMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from share.models import Share
from storage.models import Drive

User: AbstractBaseUser = get_user_model()


class DriveNotification(TimestampUUIDMixin):

    publisher = models.ForeignKey(
        User, related_name="published_notifications", on_delete=models.CASCADE
    )
    drive = models.ForeignKey(
        Drive, related_name="notifications", on_delete=models.CASCADE
    )
    share = models.OneToOneField(
        Share,
        related_name="user_notifications",
        default=None,
        on_delete=models.CASCADE,
    )
    read_by = models.ManyToManyField(User, related_name="read_notification")
