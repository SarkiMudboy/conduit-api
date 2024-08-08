from abstract.views import BaseResourceView
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.response import Serializer
from storage.models import Drive
from storage.serializers import DriveDetailSerializer, DriveSerializer


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

    def get_object(self) -> Drive:
        return self.queryset.get(uid=self.kwargs.get(self.lookup_field))

    def perform_destroy(self, instance):
        """Sets the drive to inactive"""
        instance.is_active = False
        instance.save()


class ObjectViewSet(
    RetrieveModelMixin, ListModelMixin, DestroyModelMixin, BaseResourceView
):
    ...


class DriveMemberView(RetrieveModelMixin, ListModelMixin, BaseResourceView):
    ...
