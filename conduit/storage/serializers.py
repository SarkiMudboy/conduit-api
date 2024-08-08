from typing import List

from rest_framework import serializers

from .models import Drive, Object


class UserDriveSerializer(serializers.ModelSerializer):

    size = serializers.SerializerMethodField()

    class Meta:
        model = Drive
        fields = ["uid", "name", "size"]

    def get_size(self, drive: Drive) -> str:
        drive_size = drive.size / 1000000.0
        return str(drive_size) + "GB"


class DriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drive
        fields = ["uid", "name", "size", "used", "type"]


class DriveObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ["uid", "name", "size", "metadata", "path"]


class DriveDetailSerializer(serializers.ModelSerializer):

    members = serializers.SerializerMethodField()  # first three
    objects = DriveObjectSerializer(many=True, read_only=True)

    class Meta:
        model = Drive
        fields = ["uid", "name", "size", "used", "members", "objects"]

    def get_members(self, drive: Drive) -> List[str]:
        return drive.members.values_list("tag", flat=True)[:3]
