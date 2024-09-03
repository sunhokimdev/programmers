from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.type == "A":
            return True
        return False


class IsNormal(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.type == "N":
            return True
        return False
