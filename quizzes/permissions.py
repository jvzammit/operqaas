from rest_framework.permissions import BasePermission


class IsOwnerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return hasattr(request.user, "owner")


class IsParticipantPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return hasattr(request.user, "participant")
