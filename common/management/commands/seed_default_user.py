from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from access_control.models import (
    Role,
    UserRole,
    RolePermission,
    UserPermission,
)


class Command(BaseCommand):
    help = "Seed default admin user, role, and permissions"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        self.stdout.write(self.style.NOTICE("Seeding default admin user..."))

        # -----------------------------
        # CREATE ADMIN USER
        # -----------------------------
        user, created = User.objects.get_or_create(
            employee_code="ADMIN001",
            defaults={
                "full_name": "System Admin",
                "email": "admin@example.com",
                "is_active": True,
            }
        )

        if created:
            user.set_password("Admin@123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Admin user created"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists"))

        # -----------------------------
        # CREATE ADMIN ROLE
        # -----------------------------
        role, _ = Role.objects.get_or_create(
            name="ADMIN",
            defaults={
                "is_active": True,
                "created_by": user,
                "updated_by": user,
            }
        )

        # -----------------------------
        # ASSIGN ROLE TO USER
        # -----------------------------
        UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={"is_superadmin": True}
        )

        # -----------------------------
        # PERMISSIONS
        # -----------------------------
        permissions = {
            "USER.VIEW": True,
            "USER.ADD": True,
            "USER.EDIT": True,
            "USER.DELETE": True,

            "ROLE.VIEW": True,
            "ROLE.ADD": True,
            "ROLE.EDIT": True,

            "PROJECT.VIEW": True,
            "PROJECT.ADD": True,
            "PROJECT.EDIT": True,

            "AUDIT.VIEW": True,
        }

        RolePermission.objects.update_or_create(
            role=role,
            defaults={"permissions": permissions}
        )

        UserPermission.objects.update_or_create(
            user=user,
            defaults={"permissions": permissions}
        )

        self.stdout.write(self.style.SUCCESS("Permissions assigned"))
        self.stdout.write(self.style.SUCCESS("Seeder completed successfully"))
