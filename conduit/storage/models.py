from abstract.models import TimestampUUIDMixin
from django.db import models

# from users.views import User
from django.utils.translation import gettext_lazy as _
from storage.choices import DriveType


def upload_file_to_user_drive(file: "Object", filename: str) -> str:
    """Dir for upload"""
    return f"{file.drive.owner.tag}/{file.drive.name}/files/{filename}"


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
    members = models.ManyToManyField("users.User")
    bucket = models.ForeignKey(
        "Bucket", related_name="drive", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner"],
                condition=models.Q(type="PERSONAL"),
                name="unique_personal_drive_per_user",
            )
        ]

    def __str__(self) -> str:
        return self.name


class Bucket(TimestampUUIDMixin):

    owner = models.ForeignKey(
        "users.User", related_name="bucket", on_delete=models.CASCADE
    )
    name = models.CharField(
        _("AWS bucket name"), max_length=2000, null=True, blank=True
    )
    url = models.URLField(_("AWS bucket URL"), null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Object(TimestampUUIDMixin):
    """Represents the file or folder to be stored"""

    name = models.CharField(_("File/Folder name"), max_length=2000)
    is_directory = models.BooleanField(default=False)
    drive = models.ForeignKey(
        Drive, related_name="storage_object", on_delete=models.CASCADE
    )
    file = models.FileField(
        _("File"), null=True, blank=True, upload_to=upload_file_to_user_drive
    )
    path = models.CharField(_("AWS path : key"), max_length=2000, null=True, blank=True)
    filesystem_path = models.CharField(
        _("Local path"), max_length=2000, null=True, blank=True
    )
    metadata = models.JSONField(_("File metadata"), default=dict)
    size = models.FloatField(
        _("Size of the file/directory (kb)"), null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name + " - " + self.drive.name
