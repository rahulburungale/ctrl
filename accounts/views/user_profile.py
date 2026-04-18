from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from access_control.rbac import get_user_permission_keys, is_superadmin
from departments.models import Department, Division
from designations.models import Designation
from access_control.models import (
    UserRole,
    DepartmentAccess,
    DivisionAccess,
    ClientAccess
)
from common.response import APIResponse
from drf_spectacular.utils import extend_schema
from accounts.serializers import (
    ProfileUpdateSerializer,
    ResetPasswordSerializer,
    UpdatePasswordSerializer,
    UserPermissionResponseSerializer,
)


class UserProfileAPI(APIView):
    """
    Returns logged-in user's permissions, roles & access
    """
    permission_classes = [IsAuthenticated]
    
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

        permissions = {
            permission_key: True
            for permission_key in sorted(get_user_permission_keys(user))
        }

        # Department access
        department_access = list(
            DepartmentAccess.objects.filter(user=user)
            .values_list("department_id", flat=True)
        )

        division_access = list(
            DivisionAccess.objects.filter(user=user)
            .values_list("division_id", flat=True)
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
                "department_id": user.department_id,
                "department_name": _department_name(user.department_id),
                "division_id": user.division_id,
                "division_name": _division_name(user.division_id),
                "designation_id": user.designation_id,
                "designation_name": _designation_name(user.designation_id),
                "is_active": user.is_active,
            },
            "roles": roles,
            "permissions": permissions,
            "department_access": department_access,
            "division_access": division_access,
            "client_access": client_access,
            "is_superadmin": is_superadmin(user),
        }

        return APIResponse.success(
            message="User details fetched successfully",
            data=data
        )


class ProfileUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ProfileUpdateSerializer)
    def put(self, request):
        serializer = ProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success(
            message="Profile updated successfully",
            data=serializer.data,
        )

    @extend_schema(request=ProfileUpdateSerializer)
    def patch(self, request):
        return self.put(request)


class UpdatePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UpdatePasswordSerializer)
    def post(self, request):
        serializer = UpdatePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.updated_by = request.user
        request.user.save(update_fields=["password", "updated_by", "updated_at"])
        update_session_auth_hash(request, request.user)

        return APIResponse.success(message="Password updated successfully")


class ResetPasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.updated_by = request.user
        request.user.save(update_fields=["password", "updated_by", "updated_at"])
        update_session_auth_hash(request, request.user)

        return APIResponse.success(message="Password reset successfully")


def _department_name(department_id):
    department = Department.objects.filter(pk=department_id).first()
    return department.name if department else None


def _division_name(division_id):
    division = Division.objects.filter(pk=division_id).first()
    return division.name if division else None


def _designation_name(designation_id):
    designation = Designation.objects.filter(pk=designation_id).first()
    return designation.name if designation else None
