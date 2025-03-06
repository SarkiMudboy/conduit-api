from django.db import models
from django.db.models import QuerySet
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated

# from rest_framework.status import HTTP_201_CREATED
# from rest_framework.views import Http404, status
from rest_framework.viewsets import GenericViewSet

from .models import DriveNotification
from .serializers import NotificationSerializer


class DriveNotificationView(ListModelMixin, GenericViewSet):

    queryset = DriveNotification.objects.select_related("publisher", "drive", "share")
    permission_class = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self) -> QuerySet:

        unread_notifications = self.queryset.filter(
            models.Q(drive__members=self.request.user)
            | models.Q(drive__owner=self.request.user)
        ).exclude(
            models.Q(read_by=self.request.user) & models.Q(publisher=self.request.user)
        )

        return models.QuerySet([notif.share for notif in unread_notifications])
