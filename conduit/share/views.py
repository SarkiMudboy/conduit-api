from django.http import HttpRequest
from django.shortcuts import HttpResponse
from rest_framework.decorators import action
from rest_framework.exceptions import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from storage.models import Drive
from storage.permissions import IsDriveOwnerOrMember

from .serializers import UploadPresignedURLSerializer


class ShareViewSet(ViewSet):

    serializer_class = UploadPresignedURLSerializer
    permission_classes = [IsAuthenticated, IsDriveOwnerOrMember]
    queryset = (
        Drive.objects.prefetch_related("members")
        .select_related("owner")
        .filter(is_active=True)
    )

    def get_object(self) -> Drive:
        drive = self.queryset.get(pk=self.kwargs.get("drives_uid"))
        self.check_object_permissions(self.request, drive)
        return drive

    @action(methods=["POST"], detail=False, url_path="get-upload-url")
    def get_upload_url(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        serializer = self.serializer_class(
            data=request.data,
            context={"drive": self.get_object(), "owner": request.user},
        )
        serializer.is_valid(raise_exception=True)
        url = serializer.get_url()
        return Response(data={"url": url}, status=status.HTTP_200_OK)
