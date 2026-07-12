"""
Role-based permission classes for the platform.

These are the single source of truth for access control (§13).
Permission logic must never be duplicated — always use these classes.
"""

from rest_framework.permissions import BasePermission

from users.models import UserRole


class IsEmployee(BasePermission):
    """
    Allows access to any authenticated user.

    All roles (employee, editor, admin) have at least employee-level access.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsEditor(BasePermission):
    """
    Allows access to editors and admins.

    Editors can create/edit own content and submit for approval.
    Admins inherit all editor permissions.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in (UserRole.EDITOR, UserRole.ADMIN)


class IsAdmin(BasePermission):
    """
    Allows access to admin users only.

    Admins can approve/reject content, manage categories, tags, and users.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == UserRole.ADMIN
