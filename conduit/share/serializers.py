from typing import Optional

from abstract.apis.aws.handlers import S3AWSHandler
from rest_framework import serializers
from storage.models import Object


class FileDataSerializer(serializers.Serializer):

    id = serializers.CharField(max_length=36, required=True)
    filename = serializers.CharField(max_length=2000)
    filesize = serializers.IntegerField(required=True)
    path = serializers.CharField(max_length=2000, required=True)
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

    def get_fields(self):

        fields = super().get_fields()
        if fields.get("resource"):
            filters = {
                # we may add more filters later
                "drive__uid": self.context.get("drive").uid,
            }
            fields["resource"].queryset = Object.objects.filter(**filters)
        return fields

    def get_url(self) -> str:

        objs = self.validated_data.get("files")
        root = f'{self.context.get("drive")}/'
        if self.validated_data.get("resource"):
            object: Optional[Object] = self.validated_data.get("resource")
            root = object.get_file_path(root)
        handler = S3AWSHandler()
        return handler.fetch_urls(objs, root)
