from abstract.models import TimestampUUIDMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from storage.models import Drive, Object

User: AbstractBaseUser = get_user_model()


class Share(TimestampUUIDMixin):

    author = models.ForeignKey(
        User, related_name="uploads", on_delete=models.DO_NOTHING
    )
    drive = models.ForeignKey(Drive, related_name="shares", on_delete=models.DO_NOTHING)
    assets = models.ManyToManyField(Object)
    parent = models.ForeignKey(
        Object, related_name="root_share", null=True, on_delete=models.CASCADE
    )
    note = models.CharField(_("Upload Message"), max_length=3000, null=True, blank=True)
    mentioned_members = models.ManyToManyField(User)
