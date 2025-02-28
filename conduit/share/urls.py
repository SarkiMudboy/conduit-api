from django.urls import path

from .views import StorageObjectEventWebhookView

# webhook
urlpatterns = [
    path(
        "process-storage-event/",
        StorageObjectEventWebhookView.as_view(),
        name="storage-event",
    )
]
