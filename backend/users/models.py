"""
User model for Corporate Knowledge Platform.

Extends Django's AbstractUser with a role field to support
the three-role system: Employee, Editor, Admin (§4).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    """User roles as defined in the spec (§4)."""

    EMPLOYEE = "employee", "Employee"
    EDITOR = "editor", "Editor"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    """
    Custom user model with role-based access control.

    Roles:
        - Employee: read-only access to published content.
        - Editor: create/edit own drafts, submit for approval.
        - Admin: full access including approval, user management.

    Assumption: The original brief's "Approver" role is merged into Admin
    for MVP simplicity.
    """

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.EMPLOYEE,
        db_index=True,
        help_text="Determines user permissions across the platform.",
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_employee(self):
        return self.role == UserRole.EMPLOYEE

    @property
    def is_editor(self):
        return self.role == UserRole.EDITOR

    @property
    def is_admin_user(self):
        """Named is_admin_user to avoid clash with Django's is_admin."""
        return self.role == UserRole.ADMIN
