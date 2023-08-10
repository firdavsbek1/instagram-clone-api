from rest_framework.permissions import BasePermission


class IsAdminIsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        user=request.user
        return obj.author == user or user.is_staff

    def has_permission(self, request, view):
        user=request.user
        if user and user.is_authenticated:
            return True
        return False
