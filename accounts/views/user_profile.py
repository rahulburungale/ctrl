from rest_framework.views import APIView
from access_control.permissions import HasPermission
from accounts.models import User
from access_control.models import (
    UserRole,
    RolePermission,
    UserPermission,
    DepartmentAccess,
    ClientAccess
)
from common.response import APIResponse
from drf_spectacular.utils import extend_schema
from accounts.serializers import UserPermissionResponseSerializer


class UserProfileAPI(APIView):
    """
    Returns logged-in user's permissions, roles & access
    """
    permission_classes = [HasPermission]
    
    module = "USER"

    @extend_schema(request=UserPermissionResponseSerializer)
    def get(self, request):
        self.action = "VIEW"

        user = request.user

        # Roles
        roles = list(
            UserRole.objects.filter(user=user)
            .select_related("role")
            .values_list("role__name", flat=True)
        )

        # Permissions (merge role + user permissions)
        permissions = {}

        # Role permissions
        for rp in RolePermission.objects.filter(role__userrole__user=user):
            permissions.update(rp.permissions)

        # User specific permissions (override)
        user_perm = UserPermission.objects.filter(user=user).first()
        if user_perm:
            permissions.update(user_perm.permissions)

        # Department access
        department_access = list(
            DepartmentAccess.objects.filter(user=user)
            .values_list("department_id", flat=True)
        )

        # Client access
        client_access = list(
            ClientAccess.objects.filter(user=user)
            .values_list("client_id", flat=True)
        )

        data = {
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "employee_code": user.employee_code,
                "is_active": user.is_active,
            },
            "roles": roles,
            "permissions": permissions,
            "department_access": department_access,
            "client_access": client_access,
        }

        return APIResponse.success(
            message="User details fetched successfully",
            data=data
        )
