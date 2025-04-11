from typing import List, Optional

from abstract.apis.aws.handlers import S3AWSHandler
from abstract.apis.aws.types import BaseFileObject
from abstract.models import TimestampUUIDMixin
from django.db import models
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
    size = models.FloatField(
        _("Drive size (kb)"),
        default=float(5 * 1024 * 1024 * 1024),
        null=True,
        blank=True,
    )
    used = models.FloatField(_("Space used (kb)"), default=0.0, null=True, blank=True)
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
            self.pk is None
            and self.type == DriveType.PERSONAL
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
        _("AWS path : key"),
        default="new",
        max_length=2000,
        null=True,
        blank=True,
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

    def get_file_path(self) -> str:
        """Dir for upload"""
        return self.path + "/"

    def get_download_path(self, root: Optional[str] = None) -> str:
        """Full path for download"""

        full_path = self.path[1:]
        if root:
            splitted_path = full_path.split(root)
            full_path = root + splitted_path[-1]

        return full_path

    def get_object_download_url(self) -> List[BaseFileObject]:
        """directory assets are recursively fetched from db,
        while obtaining the presigned urls at the same time.
        return: List of FileObject types.
        """

        if not self.is_directory:
            return [
                {
                    "id": self.pk,
                    "path": self.get_download_path(),
                    "url": self._get_object_download_url(),
                }
            ]

        return fetch_all_folder_asset_from_db(
            self, [], self.name if self.in_directory else None
        )

    def _get_object_download_url(self) -> str:

        handler = S3AWSHandler()
        return handler.get_download_presigned_url(self.drive.name + self.path)


def fetch_all_folder_asset_from_db(
    asset: Object, tree: List[BaseFileObject], root: str
) -> List[BaseFileObject]:

    # recursive func to get all the contents of the folder from db...
    content = asset.content.all()
    if not content:
        tree.append(
            {
                "id": asset.pk,
                "path": asset.get_download_path(root),
                "url": asset._get_object_download_url(),
            }
        )
        return tree

    for obj in content:
        tree = fetch_all_folder_asset_from_db(obj, tree, root)

    return tree
