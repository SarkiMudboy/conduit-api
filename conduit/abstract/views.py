from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .filters import IsOwnerFilterBackend
from .permissions import IsOwner


class BaseResourceView(GenericViewSet):

    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [IsOwnerFilterBackend]
