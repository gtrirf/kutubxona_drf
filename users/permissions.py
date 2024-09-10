from rest_framework import permissions
from .models import RoleCodes

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with the 'admin' role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleCodes.ADMIN


class IsStaff(permissions.BasePermission):
    """
    Allows access to 'staff' users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleCodes.STAFF


class IsUser(permissions.BasePermission):
    """
    Allow access to 'user' users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleCodes.USER


class IsDirector(permissions.BasePermission):
    """
    Allow access to 'director' users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == RoleCodes.DIRECTOR