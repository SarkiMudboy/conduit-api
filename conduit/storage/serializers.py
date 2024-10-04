from typing import Any, Dict, List

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
        fields = ["uid", "name", "size", "metadata", "path", "is_directory"]


class DriveDetailSerializer(serializers.ModelSerializer):

    members = serializers.SerializerMethodField()  # first three
    storage_objects = serializers.SerializerMethodField()

    class Meta:
        model = Drive
        fields = ["uid", "name", "size", "used", "members", "storage_objects"]

    def get_members(self, drive: Drive) -> List[str]:
        return drive.members.values_list("tag", flat=True)[:3]

    def get_storage_objects(self, drive: Drive) -> Dict[str, Any]:
        objects = drive.storage_object.filter(in_directory__isnull=True)
        return DriveObjectSerializer(objects, many=True).data


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


class ObjectDetailSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()

    class Meta:
        model = Object
        fields = ["uid", "name", "size", "content", "metadata", "path"]

    def get_content(self, object: Object) -> Dict[str, Any]:
        """Nested content for directories: 1 layer deep"""
        depth = self.context.get("depth", 2)
        objects = object.content.all()
        if depth > 1:
            return DriveObjectSerializer(objects, many=True, context={"depth": -1}).data
        return None
