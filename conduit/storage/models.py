from typing import Optional

from abstract.models import TimestampUUIDMixin
from django.db import models

# from users.views import User
from django.utils.translation import gettext_lazy as _
from storage.choices import DriveType


def upload_file_to_user_drive(file: "Object", filename: str) -> str:
    """Dir for upload"""
    return f"{file.drive.owner.tag}/{file.drive.name}/{file.path}/{filename}"


class Drive(TimestampUUIDMixin):
    """Each drive is a cloud storage for the user: It can be personal/shared"""

    owner = models.ForeignKey(
        "users.User", related_name="user_drive", on_delete=models.CASCADE
    )
    name = models.CharField(_("Drive's name"), max_length=2000, null=True, blank=True)
    type = models.CharField(
        _("Drive type"), choices=DriveType.choices, default=DriveType.SHARED
    )
    size = models.FloatField(_("Drive size (kb)"), null=True, blank=True)
    used = models.FloatField(_("Space used (kb)"), null=True, blank=True)
    members = models.ManyToManyField("users.User")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner"],
                condition=models.Q(type="personal"),
                name="unique_personal_drive_per_user",
            )
        ]

    def save(self, *args, **kwargs):
        """Verify that the drive is unique for personal"""

        if (
            self.type == DriveType.PERSONAL
            and Drive.objects.filter(owner=self.owner, type=DriveType.PERSONAL).exists()
        ):
            raise ValueError("A user can only have one personal drive.")

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Object(TimestampUUIDMixin):
    """Represents the file or folder to be stored"""

    owner = models.ForeignKey(
        "users.User",
        related_name="storage_object",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField(_("File/Folder name"), max_length=2000)
    is_directory = models.BooleanField(default=False)  # may need to remove this
    drive = models.ForeignKey(
        Drive, related_name="storage_object", on_delete=models.CASCADE
    )
    file = models.FileField(
        _("File"), null=True, blank=True, upload_to=upload_file_to_user_drive
    )
    content = models.ManyToManyField(
        "self", blank=True, related_name="in_directory", symmetrical=False
    )
    path = models.CharField(
        _("AWS path : key"), default="new", max_length=2000, null=True, blank=True
    )
    filesystem_path = models.CharField(
        _("Local path"), max_length=2000, null=True, blank=True
    )
    metadata = models.JSONField(_("File metadata"), default=dict)
    size = models.FloatField(
        _("Size of the file/directory (kb)"), null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name + " - " + self.drive.name

    def get_file_path(self, new_filepath: str, author: Optional[str] = None) -> str:
        """Dir for upload"""
        if not author:
            author = self.owner.tag
        return f"{author}/{self.drive.name}/{self.path}/{new_filepath}"
