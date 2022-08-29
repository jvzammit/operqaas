from rest_framework.permissions import SAFE_METHODS, BasePermission


class QuizPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return True
        if hasattr(request.user, "owner"):
            owner = request.user.owner
            quiz_id_list = owner.quiz_set.all().values_list("id", flat=True)
            return obj.id in quiz_id_list
        return False


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
