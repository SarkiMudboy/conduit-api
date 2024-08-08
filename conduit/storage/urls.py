from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import DriveMemberView, DriveViewSet, ObjectViewSet

router = DefaultRouter()
router.register(r"", DriveViewSet, basename="drives")

drive_router = routers.NestedSimpleRouter(router, r"", lookup="drives")
drive_router.register(r"objects", ObjectViewSet, basename="objects")
drive_router.register(r"members", DriveMemberView, basename="members")

urlpatterns = [*router.urls, *drive_router.urls]
