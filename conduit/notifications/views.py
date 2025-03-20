from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import HttpResponse
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import DriveNotification
from .serializers import NotificationSerializer, NotifUpdateSerializer


class DriveNotificationView(ListModelMixin, GenericViewSet):

    queryset = DriveNotification.objects.select_related("publisher", "drive", "share")
    permission_class = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self) -> QuerySet:

        user = self.request.user

        notifications = self.queryset.filter(
            models.Q(drive__members=self.request.user)
            | models.Q(drive__owner=self.request.user)
        )

        notif_ids = user.read_notification.values_list("pk", flat=True)
        unread_notifications = notifications.exclude(uid__in=notif_ids)

        return [notif.share for notif in unread_notifications]

    @action(methods=["POST"], detail=True, url_path="mark-read")
    def mark_notif_as_read(self, request: HttpRequest, pk: str) -> HttpResponse:

        notification = get_object_or_404(DriveNotification, share__pk=pk)
        serializer = NotifUpdateSerializer(
            notification, context={"publisher": request.user}
        )
        serializer.save()
        return Response(200)
