from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from rest_framework import serializers
from share.models import Share
from storage.models import Drive

from .models import DriveNotification

User: AbstractBaseUser = get_user_model()


class BaseDriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drive
        fields = ["uid", "name"]


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uid", "tag"]


class NotificationSerializer(serializers.ModelSerializer):

    drive = BaseDriveSerializer()
    author = BaseUserSerializer()
    source = serializers.SerializerMethodField()

    class Meta:
        model = Share
        fields = ["uid", "drive", "assets", "author", "source", "note", "created_at"]

    def get_source(self, instance) -> Optional[str]:
        if instance.parent:
            return instance.parent.uid
        return None


class NotifUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model: DriveNotification

    def save(self) -> DriveNotification:

        instance = self.instance
        user = self.context.get("publisher")

        instance.read_by.add(user)
        return instance
