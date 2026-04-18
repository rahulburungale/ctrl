from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from access_control.models import (
    Permission,
    Role,
    RolePermission,
    UserPermission,
    UserRole,
)


ALL_PERMISSION_KEYS = [
    "user.view",
    "user.create",
    "user.update",
    "user.delete",
    "user.restore",
    "role.view",
    "role.create",
    "role.update",
    "permission.view",
    "permission.create",
    "permission.update",
    "client.view",
    "client.create",
    "client.update",
    "client.delete",
    "client.restore",
    "department.view",
    "department.create",
    "department.update",
    "department.delete",
    "department.restore",
    "division.view",
    "division.create",
    "division.update",
    "division.delete",
    "division.restore",
    "designation.view",
    "designation.create",
    "designation.update",
    "designation.delete",
    "designation.restore",
    "project.view",
    "project.create",
    "project.update",
    "project.delete",
    "project.restore",
    "audit.view",
    "login_log.view",
]

ROLE_PERMISSIONS = {
    # Full RBAC-controlled access. SuperAdmin bypass is separate on UserRole.
    "Admin": ALL_PERMISSION_KEYS,
    # HOD visibility is scoped by DepartmentAccess/user.department_id in RBAC filters.
    "HOD": [
        "user.view",
        "client.view",
        "department.view",
        "division.view",
        "designation.view",
        "project.view",
        "project.create",
        "project.update",
        "project.restore",
    ],
    # Managers can work only on projects reachable through assignment/access filters.
    "Manager": [
        "user.view",
        "client.view",
        "department.view",
        "division.view",
        "project.view",
        "project.update",
        "project.restore",
    ],
    # Team Leaders can view/update assigned projects and manage members within them.
    "Team Leader": [
        "user.view",
        "project.view",
        "project.update",
    ],
    "Sales Team": [
        "client.view",
        "department.view",
        "division.view",
        "project.view",
    ],
    # Production roles are intentionally read-only at API level by default.
    "Detailer": [
        "project.view",
    ],
    "Modeller": [
        "project.view",
    ],
    "Checker": [
        "project.view",
    ],
}


class Command(BaseCommand):
    help = "Seed default SuperAdmin user, base roles, and canonical permissions"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        self.stdout.write(self.style.NOTICE("Seeding default SuperAdmin and RBAC roles..."))

        # -----------------------------
        # CREATE DEFAULT SUPERADMIN USER
        # -----------------------------
        user, created = User.objects.get_or_create(
            employee_code="0001",
            defaults={
                "full_name": "System Admin",
                "email": "admin@pangulftech.com",
                "is_active": True,
            }
        )

        if created:
            user.set_password("admin123")
            user.save()
            self.stdout.write(self.style.SUCCESS("SuperAdmin user created"))
        else:
            self.stdout.write(self.style.WARNING("SuperAdmin user already exists"))

        # -----------------------------
        # PERMISSION CATALOG
        # -----------------------------
        for permission_key in ALL_PERMISSION_KEYS:
            Permission.objects.get_or_create(
                name=permission_key,
                defaults={
                    "is_active": True,
                    "created_by": user,
                    "updated_by": user,
                },
            )

        # -----------------------------
        # BASIC ROLES + ROLE PERMISSIONS
        # -----------------------------
        roles = {}
        for role_name, permission_keys in ROLE_PERMISSIONS.items():
            role = self._get_or_create_role(role_name, user)
            roles[role_name] = role

            permissions = {permission_key: True for permission_key in permission_keys}
            RolePermission.objects.update_or_create(
                role=role,
                defaults={"permissions": permissions}
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Role seeded: {role.name} ({len(permission_keys)} permissions)"
                )
            )

        # -----------------------------
        # ASSIGN SUPERADMIN ROLE/BYPASS
        # -----------------------------
        UserRole.objects.update_or_create(
            user=user,
            role=roles["Admin"],
            defaults={"is_superadmin": True}
        )

        UserPermission.objects.update_or_create(
            user=user,
            defaults={"permissions": {key: True for key in ALL_PERMISSION_KEYS}}
        )

        self.stdout.write(self.style.SUCCESS("Default SuperAdmin credentials: 0001 / admin123"))
        self.stdout.write(self.style.SUCCESS("Role access scope is enforced by DepartmentAccess, ClientAccess, and ProjectTeamMember assignments."))
        self.stdout.write(self.style.SUCCESS("Seeder completed successfully"))

    def _get_or_create_role(self, role_name, user):
        role = Role.objects.filter(name__iexact=role_name).first()
        if role:
            if role.name != role_name or not role.is_active:
                role.name = role_name
                role.is_active = True
                role.updated_by = user
                role.save(update_fields=["name", "is_active", "updated_by", "updated_at"])
            return role

        return Role.objects.create(
            name=role_name,
            is_active=True,
            created_by=user,
            updated_by=user,
        )
