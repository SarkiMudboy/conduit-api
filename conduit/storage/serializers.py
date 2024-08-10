from typing import List

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers

from .models import Drive, Object

User: AbstractBaseUser = get_user_model()


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
    storage_object = DriveObjectSerializer(many=True, read_only=True)

    class Meta:
        model = Drive
        fields = ["uid", "name", "size", "used", "members", "storage_object"]

    def get_members(self, drive: Drive) -> List[str]:
        return drive.members.values_list("tag", flat=True)[:3]


class AddDriveMemberSerializer(serializers.ModelSerializer):

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True, is_superuser=False), many=True
    )

    class Meta:
        model = Drive
        fields = ["members"]

    def update(self, instance, validated_data):
        instance.members.add(*validated_data["members"])
        return instance


class DriveMemberSerializer(serializers.ModelSerializer):

    # add shares later here...
    class Meta:
        model = User
        fields = ["uid", "tag", "avatar"]
        read_only_fields = ["uid", "tag", "avatar"]
