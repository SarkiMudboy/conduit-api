from django.http import HttpRequest
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to view/edit it.
    """

    def has_object_permission(self, request: HttpRequest, view, obj) -> bool:
        return obj.owner == request.user
