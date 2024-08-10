from rest_framework.permissions import BasePermission


class IsDriveOwnerOrMember(BasePermission):

    message: str = "You do not have access to this drive"

    def has_object_permission(self, request, view, obj) -> bool:
        return obj.owner == request.user or request.user in obj.members.all()


class IsDriveOwner(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if view.action in ["create", "destroy"]:
            return obj.owner == request.user

        return True
