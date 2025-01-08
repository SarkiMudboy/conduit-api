from django.urls import path

from .views import StorageObjectEventWebhookView

# webhook
urlpatterns = [
    path(
        "process-strorage-event/",
        StorageObjectEventWebhookView.as_view(),
        name="storage-event",
    )
]
