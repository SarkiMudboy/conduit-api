from django.urls import path

from .views import DriveNotificationView

get_notifications = DriveNotificationView.as_view({"get": "list"})

urlpatterns = [path("", get_notifications, name="drive-notification")]
