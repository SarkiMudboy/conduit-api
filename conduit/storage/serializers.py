from rest_framework import serializers

from .models import Drive


class UserDriveSerializer(serializers.ModelSerializer):

    size = serializers.SerializerMethodField()

    class Meta:
        model = Drive
        fields = ["uid", "name", "size"]

    def get_size(self, drive: Drive) -> str:
        drive_size = drive.size / 1000000.0
        return str(drive_size) + "GB"
