from abstract.apis.aws.handlers import S3AWSHandler
from rest_framework import serializers
from storage.models import Object


class FileDataSerializer(serializers.Serializer):

    filename = serializers.CharField(max_length=2000)
    filesize = serializers.DecimalField(decimal_places=2)


class UploadPresignedURLSerializer(serializers.Serializer):

    file = FileDataSerializer(required=True)
    resource_uid = serializers.PrimaryKeyRelatedField(
        queryset=Object.objects.filter(),  # ensure this is owned by owner
        required=False,
    )

    def get_url(self) -> str:

        filename = self.validated_data.file.name
        handler = S3AWSHandler()
        return handler.get_upload_presigned_url(filename)
