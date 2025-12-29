from rest_framework.permissions import BasePermission
from access_control.models import UserRole, RolePermission, UserPermission


class HasPermission(BasePermission):
    """
    Checks user permissions based on:
    1. Superadmin → full access
    2. Role permissions
    3. User permissions
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # SUPER ADMIN CHECK
        if UserRole.objects.filter(
            user=request.user,
            is_superadmin=True
        ).exists():
            return True

        module = getattr(view, "module", None)
        action = getattr(view, "action", None)

        if not module or not action:
            return False

        permission_key = f"{module}.{action}"

        # --- USER LEVEL PERMISSIONS ---
        user_perm = UserPermission.objects.filter(
            user=request.user
        ).first()

        if user_perm and user_perm.permissions.get(permission_key):
            return True

        # --- ROLE LEVEL PERMISSIONS ---
        roles = UserRole.objects.filter(user=request.user)

        for r in roles:
            role_perm = RolePermission.objects.filter(role=r.role).first()
            if role_perm and role_perm.permissions.get(permission_key):
                return True

        return False
