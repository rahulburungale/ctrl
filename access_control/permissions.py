from rest_framework.permissions import BasePermission

from access_control.rbac import (
    is_superadmin,
    log_permission_denied,
    permission_key_for_request,
    user_has_permission,
)


class HasPermission(BasePermission):
    """
    Central RBAC permission class.

    Resolution order:
    1. SuperAdmin users bypass all checks.
    2. Explicit view.permission_required values are used when present.
    3. Otherwise module/action is inferred from the view and HTTP method.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if is_superadmin(request.user):
            return True

        permission_key = permission_key_for_request(request, view)
        if not permission_key:
            log_permission_denied(request, "missing-permission-key")
            return False

        if user_has_permission(request.user, permission_key):
            return True

        log_permission_denied(request, permission_key)
        return False


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and is_superadmin(request.user)
        )
