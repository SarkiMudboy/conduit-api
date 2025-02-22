from typing import Dict, List, Optional

from abstract.apis.aws.handlers import S3AWSHandler
from abstract.apis.aws.types import FileMetaData
from rest_framework import serializers
from storage.models import Object

from .tasks import handle_object_event


class FileDataSerializer(serializers.Serializer):

    id = serializers.CharField(max_length=36, required=True)
    filename = serializers.CharField(max_length=2000)
    filesize = serializers.IntegerField(required=True)
    path = serializers.CharField(max_length=2000, required=True, allow_blank=True)
    # metadata

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

    def set_metadata(self) -> None:
        self._metadata = FileMetaData(
            owner_email=self.context.get("owner").email,
            drive_id=str(self.context.get("drive").pk),
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

            print(">>>->>>>", root, flush=True)
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
