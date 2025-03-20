from rest_framework.routers import DefaultRouter

from .views import DriveNotificationView

router = DefaultRouter()
router.register(r"", DriveNotificationView, basename="drive_notifications")
urlpatterns = [*router.urls]
