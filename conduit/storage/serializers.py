from typing import Any, Dict, List

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers

from .models import Drive, Object
from .utils import handle_directory_depth

User: AbstractBaseUser = get_user_model()


class UserDriveSerializer(serializers.ModelSerializer):

    size = serializers.SerializerMethodField()

    class Meta:
        model = Drive
        fields = ["uid", "name", "size"]

    def get_size(self, drive: Drive) -> str:
        drive_size = drive.size / 1000000.0
        return str(drive_size) + "GB"


class BaseDriveSerializer(serializers.ModelSerializer):

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        write_only=True,
        required=True,
        many=True,
    )

    class Meta:
        model = Drive
        fields = ["name", "members"]

    def validate_members(self, members: List[str]) -> List[str]:
        if not members:
            raise serializers.ValidationError("A drive must have at least 1 member")
        return members

    def validate_name(self, name: str) -> str:
        if Drive.objects.filter(
            owner=self.context.get("user"), name=name, is_active=True
        ).exists():
            raise serializers.ValidationError(
                "You have a drive with this name, please rename"
            )
        return name

    def create(self, validated_data):

        members = validated_data.pop("members", [])

        drive = Drive.objects.create(
            owner=self.context.get("user"),
            name=validated_data.get("name"),
            used=0.00,
        )
        drive.members.add(*members)
        return drive


class DriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drive
        fields = ["uid", "name", "size", "used", "type", "created_at"]


class DriveObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = [
            "uid",
            "name",
            "size",
            "metadata",
            "path",
            "is_directory",
            "created_at",
        ]


class DriveDetailSerializer(serializers.ModelSerializer):

    members = serializers.SerializerMethodField()  # first three
    storage_objects = serializers.SerializerMethodField()
    directories = serializers.SerializerMethodField()

    class Meta:
        model = Drive
        fields = [
            "uid",
            "name",
            "size",
            "used",
            "members",
            "storage_objects",
            "directories",
        ]

    def get_members(self, drive: Drive) -> List[str]:
        return drive.members.values_list("tag", flat=True)[:3]

    def get_storage_objects(self, drive: Drive) -> Dict[str, Any]:
        objects = drive.storage_object.filter(in_directory__isnull=True)
        return DriveObjectSerializer(objects, many=True).data

    def get_directories(self, drive: Drive):
        objects = drive.storage_object.filter(in_directory__isnull=True)
        if objects:
            dirs = handle_directory_depth(objects)
            if dirs:
                return ObjectDetailSerializer(dirs, many=True).data

        return None


class AddDriveMemberSerializer(serializers.ModelSerializer):

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True, is_superuser=False),
        many=True,
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
    directories = serializers.SerializerMethodField()

    class Meta:
        model = Object
        fields = [
            "uid",
            "name",
            "size",
            "content",
            "metadata",
            "path",
            "directories",
        ]

    def get_content(self, object: Object) -> List[Dict[str, Any]]:

        objects = object.content.all()
        return DriveObjectSerializer(objects, many=True).data

    def get_directories(self, object: Object) -> List[Dict[str, Any]]:
        # TODO: There needs to be a limit on the number of objects that this routine is run for...Ideally we do not want this to be done
        # for really large folders, so monitor latency and find that threshold that this starts to become annoying...
        objects = object.content.all()
        dirs = handle_directory_depth(objects)

        if dirs:
            return ObjectDetailSerializer(dirs, many=True).data

        return None


class ObjectPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Object
        fields = ["uid", "name"]
