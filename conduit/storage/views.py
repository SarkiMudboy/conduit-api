from abstract.exceptions import BadRequestException, UnauthorizedException
from abstract.views import BaseResourceView
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response, Serializer
from rest_framework.views import Http404, status
from rest_framework.viewsets import GenericViewSet

from .choices import DriveType
from .models import Drive, Object
from .serializers import (
    AddDriveMemberSerializer,
    DriveDetailSerializer,
    DriveMemberSerializer,
    DriveObjectSerializer,
    DriveSerializer,
)

User: AbstractBaseUser = get_user_model()


class DriveViewSet(
    RetrieveModelMixin, ListModelMixin, DestroyModelMixin, BaseResourceView
):

    queryset = (
        Drive.objects.prefetch_related("members")
        .select_related("bucket", "owner")
        .filter(is_active=True)
    )
    serializer_class = DriveSerializer
    lookup_field = "uid"

    def get_serializer_class(self) -> Serializer:
        if self.action == "retrieve":
            return DriveDetailSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        """Sets the drive to inactive"""
        if instance.type == DriveType.PERSONAL:
            raise BadRequestException("You cannot delete your drive")
        instance.is_active = False
        instance.save()


class ObjectViewSet(
    RetrieveModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Object.objects.select_related("drive")
    serializer_class = DriveObjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uid"

    def get_queryset(self) -> QuerySet:

        drive_uid = self.kwargs.get("drives_uid")
        drive = get_object_or_404(Drive, uid=drive_uid)

        if drive.owner != self.request.user:
            raise UnauthorizedException("You do not have access to this drive")

        return self.queryset.filter(drive__uid=drive_uid)

    def get_object(self) -> Object:
        try:
            return self.get_queryset().get(uid=self.kwargs.get(self.lookup_field))
        except Object.DoesNotExist:
            raise Http404("Storage object Not Found")


class DriveMemberView(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):

    queryset = User.objects.all()
    serializer_class = DriveMemberSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uid"

    def get_drive(self) -> Drive:

        drive_uid = self.kwargs.get("drives_uid")
        drive = get_object_or_404(Drive, uid=drive_uid)

        if drive.owner != self.request.user:
            raise UnauthorizedException("You do not have access to this drive")

        return drive

    def get_queryset(self) -> QuerySet:

        drive = self.get_drive()
        return drive.members.all()

    def get_object(self) -> AbstractBaseUser:

        try:
            return self.get_queryset().get(uid=self.kwargs.get(self.lookup_field))
        except User.DoesNotExist:
            raise Http404("Member Not Found")

    def create(self, request, *args, **kwargs):
        """Adds user to drive"""

        drive = self.get_drive()
        serializer = AddDriveMemberSerializer(drive, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    def perform_destroy(self, instance: AbstractBaseUser):
        """Removes user from drive"""

        drive = self.get_drive()
        drive.members.remove(instance)
