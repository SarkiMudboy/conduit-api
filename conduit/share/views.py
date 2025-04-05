import json
import urllib

from django.http import HttpRequest
from django.shortcuts import HttpResponse
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.exceptions import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from storage.models import Drive, Object
from storage.permissions import IsDriveOwnerOrMember

from .serializers import (
    DownloadPresignedURLSerializer,
    ObjectEventSerializer,
    PresignedURLSerializer,
    UploadPresignedURLSerializer,
)


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

    def get_file_object(self) -> Object:

        obj_pk = self.kwargs.get("pk")
        file_object = Object.objects.select_related("drive").get(pk=obj_pk)
        self.check_object_permissions(self.request, file_object.drive)

        return file_object

    @action(methods=["POST"], detail=False, url_path="get-upload-url")
    def get_upload_url(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        serializer = self.serializer_class(
            data=request.data,
            context={"drive": self.get_object(), "owner": request.user},
        )
        serializer.is_valid(raise_exception=True)
        urls = serializer.get_url()
        metadata = serializer.get_file_upload_metadata()

        return Response(
            {
                "presigned_urls": PresignedURLSerializer(urls, many=True).data,
                "metadata": metadata,
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=["GET"], detail=True, url_path="get-download-url")
    def get_download_url(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        asset = self.get_file_object()
        serializer = DownloadPresignedURLSerializer(asset)
        return Response(serializer.data, status.HTTP_200_OK)


class StorageObjectEventWebhookView(generics.GenericAPIView):

    serializer_class = ObjectEventSerializer
    permission_classes = [AllowAny]

    def parse_sns_event_data(self, event_data: dict) -> str:
        """
        Parses SNS message data to get the key of the storage object
        :params -> event_data: dict (AWS SNS json data)
        :returns - Key
        N.B I need to find a way to return error status codes here in case of failures so AWS can trigger a retry
        """

        key = None
        event_data = json.loads(event_data)
        event_message = json.loads(event_data["Message"])
        event_name = event_message["Records"][0]["eventName"]

        if event_name == "ObjectCreated:Put":
            print(event_data)
            key = urllib.parse.unquote_plus(
                event_message["Records"][0]["s3"]["object"]["key"],
                encoding="utf-8",
            )
            print(key, flush=True)

        return key

    def post(self, request: HttpRequest) -> HttpResponse:

        data = request.body.decode("utf-8")
        if request.headers.get("x-amz-sns-message-type") == "SubscriptionConfirmation":
            print(json.loads(data), flush=True)
        else:
            key = self.parse_sns_event_data(data)

            if key:
                serializer = self.serializer_class(data={"key": key})
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return Response(200)
