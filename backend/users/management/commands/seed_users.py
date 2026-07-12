"""
Management command to seed default users for development/demo.

Creates one user per role if they don't already exist:
  - admin / admin123    (Admin)
  - editor / editor123  (Editor)
  - employee / employee123 (Employee)
"""

from django.core.management.base import BaseCommand

from users.models import User, UserRole


SEED_USERS = [
    {
        "username": "admin",
        "email": "admin@company.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "role": UserRole.ADMIN,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "editor",
        "email": "editor@company.com",
        "password": "editor123",
        "first_name": "Editor",
        "last_name": "User",
        "role": UserRole.EDITOR,
    },
    {
        "username": "employee",
        "email": "employee@company.com",
        "password": "employee123",
        "first_name": "Employee",
        "last_name": "User",
        "role": UserRole.EMPLOYEE,
    },
]


class Command(BaseCommand):
    help = "Seed default users for development and demo purposes."

    def handle(self, *args, **options):
        for user_data in SEED_USERS:
            username = user_data["username"]
            password = user_data.pop("password")

            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_data,
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created {user.role} user: {username}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"User already exists: {username}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("\nSeeding complete."))
