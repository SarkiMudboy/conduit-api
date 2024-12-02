from typing import Optional

from abstract.apis.aws.handlers import S3AWSHandler
from rest_framework import serializers
from storage.models import Object


class FileDataSerializer(serializers.Serializer):

    filename = serializers.CharField(max_length=2000)
    filesize = serializers.IntegerField(required=True)

    # validate size and depth of dir here...


class UploadPresignedURLSerializer(serializers.Serializer):

    file = FileDataSerializer(many=True, required=True)
    resource = serializers.PrimaryKeyRelatedField(
        queryset=Object.objects.all(),
        required=False,
    )

    def get_fields(self):

        fields = super().get_fields()
        if fields.get("resource"):
            filters = {
                "owner": self.context.get("owner"),
                "drive__uid": self.context.get("drive"),
            }
            fields["resource"].queryset = Object.objects.filter(**filters)
        return fields

    def get_url(self) -> str:

        key = self.validated_data.get("file")[0]["filename"]

        # append the dir path here
        object: Optional[Object] = self.validated_data.get("resource")
        if object:
            key = object.get_file_path(key)

        key = f'{self.context.get("drive")}/{key}'
        handler = S3AWSHandler()
        return handler.get_upload_presigned_url(key)
