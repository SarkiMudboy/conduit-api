import uuid
from typing import Dict, List, Optional

from abstract.apis.aws.handlers import S3AWSHandler
from abstract.apis.aws.types import FileMetaData
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers
from storage.models import Object

from .tasks import handle_object_event

User: AbstractBaseUser = get_user_model()


class FileDataSerializer(serializers.Serializer):

    id = serializers.CharField(max_length=36, required=True)
    filename = serializers.CharField(max_length=2000)
    filesize = serializers.IntegerField(required=True)
    path = serializers.CharField(max_length=2000, required=True, allow_blank=True)

    # validate size and depth of dir here...


class PresignedURLSerializer(serializers.Serializer):

    id = serializers.CharField(max_length=36, required=True)
    url = serializers.URLField(allow_blank=True)


class UploadPresignedURLSerializer(serializers.Serializer):

    files = FileDataSerializer(many=True, required=True)
    resource = serializers.PrimaryKeyRelatedField(
        queryset=Object.objects.all(),
        required=False,
    )
    bulk = serializers.BooleanField()
    note = serializers.CharField(max_length=3000, required=False)
    mentioned_members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, many=True
    )
    _meta_data = FileMetaData()

    def get_fields(self):

        fields = super().get_fields()
        if fields.get("resource"):
            filters = {
                # we may add more filters later
                "drive__uid": self.context.get("drive").uid,
            }
            fields["resource"].queryset = Object.objects.filter(**filters)
        return fields

    def validate_mentioned_members(self, members: List[str]):

        drive = self.context.get("drive")
        for member in members:
            if uuid.UUID(member) not in drive.members.values_list("pk", flat=True):
                serializers.ValidationError("Invalid member")

    def set_metadata(self) -> None:

        note = self.validated_data.get("note")
        mentioned_members = self.validated_data.get("mentioned_members")
        recipients = mentioned_members.join(",") if mentioned_members else ""

        self._metadata = FileMetaData(
            author=str(self.context.get("owner").pk),
            drive_id=str(self.context.get("drive").pk),
            bulk=str(self.validated_data.get("bulk")),
            share_uid=str(uuid.uuid4()),
            note=note if note else "",
            mentioned_members=recipients,
        )

    def get_file_upload_metadata(self) -> Dict[str, str]:

        file_upload_metadata = {}
        for metadata in self._metadata.keys():
            file_upload_metadata["x-amz-meta-" + metadata] = self._metadata[metadata]

        return file_upload_metadata

    def get_url(self) -> List[str]:

        objs = self.validated_data.get("files")
        root = f'{self.context.get("drive")}'

        self.set_metadata()

        if self.validated_data.get("resource"):
            object: Optional[Object] = self.validated_data.get("resource")

            if not object.is_directory:
                raise serializers.ValidationError("Resource is not a directory")
            root += object.get_file_path()

            self._metadata["resource_id"] = str(object.pk)
        else:
            root += "/"

        handler = S3AWSHandler()
        return handler.fetch_urls(objs, root, self._metadata)


class ObjectEventSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=1000, required=True)

    def save(self) -> None:
        """Launch task here
        call the task.delay here and immediately return
        """
        handle_object_event.delay(self.validated_data.get("key"))
        return
