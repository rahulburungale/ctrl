from rest_framework.views import APIView
from access_control.permissions import HasPermission
from access_control.rbac import filter_queryset_for_user
from accounts.models import User
from accounts.serializers import UserCreateSerializer
from clients.models import Client
from common.response import APIResponse
from common.pagination import OptionalPagination
from departments.models import Department, Division
from drf_spectacular.utils import extend_schema


class UserAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "user"
    module = "USER"

    def get(self, request):
        self.action = "VIEW"

        queryset = User.objects.filter(is_active=True)
        queryset = filter_queryset_for_user(request.user, queryset, "user")

        paginator = OptionalPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)

        if paginated_data:
            return paginator.get_paginated_response(
                UserCreateSerializer(paginated_data, many=True).data
            )
        
        return APIResponse.success(
            data=UserCreateSerializer(queryset, many=True).data
        )
    
    @extend_schema(request=UserCreateSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not _has_requested_access_scope(request, serializer.validated_data):
            return APIResponse.error("Invalid department or client access", 403)
        serializer.save(created_by=request.user)

        return APIResponse.success(
            message="User created successfully",
            data=serializer.data
        )


class UserDetailAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "user"
    module = "USER"
    permission_required = {
        "PUT": "user.update",
        "PATCH": "user.restore",
        "DELETE": "user.delete",
    }

    @extend_schema(request=UserCreateSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        user = filter_queryset_for_user(
            request.user,
            User.objects.filter(pk=pk),
            "user",
        ).first()
        if not user:
            return APIResponse.error("User not found", 404)

        serializer = UserCreateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if not _has_requested_access_scope(request, serializer.validated_data, user):
            return APIResponse.error("Invalid department or client access", 403)
        serializer.save(updated_by=request.user)

        return APIResponse.success(
            message="User updated successfully",
            data=serializer.data
        )
    
    def delete(self, request, pk):
        self.action = "DELETE"

        user = filter_queryset_for_user(
            request.user,
            User.objects.filter(pk=pk),
            "user",
        ).first()
        if not user:
            return APIResponse.error("User not found", 404)

        user.is_active = False
        user.updated_by = request.user
        user.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("User deactivated successfully")

    def patch(self, request, pk):
        """
        Restore user
        """
        self.action = "RESTORE"

        user = filter_queryset_for_user(
            request.user,
            User.objects.filter(pk=pk),
            "user",
        ).first()
        if not user:
            return APIResponse.error("User not found", 404)

        user.is_active = True
        user.updated_by = request.user
        user.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("User restored successfully")


def _has_requested_access_scope(request, validated_data, instance=None):
    department_id = validated_data.get(
        "department_id",
        getattr(instance, "department_id", None),
    )
    if department_id:
        department_allowed = filter_queryset_for_user(
            request.user,
            Department.objects.filter(pk=department_id),
            "department",
        ).exists()
        if not department_allowed:
            return False

    division_id = validated_data.get(
        "division_id",
        getattr(instance, "division_id", None),
    )
    if division_id:
        division_allowed = filter_queryset_for_user(
            request.user,
            Division.objects.filter(pk=division_id),
            "division",
        ).exists()
        if not division_allowed:
            return False

    department_access = validated_data.get("department_access")
    if department_access:
        allowed_count = filter_queryset_for_user(
            request.user,
            Department.objects.filter(pk__in=department_access),
            "department",
        ).count()
        if allowed_count != len(set(department_access)):
            return False

    division_access = validated_data.get("division_access")
    if division_access:
        allowed_count = filter_queryset_for_user(
            request.user,
            Division.objects.filter(pk__in=division_access),
            "division",
        ).count()
        if allowed_count != len(set(division_access)):
            return False

    client_access = validated_data.get("client_access")
    if client_access:
        allowed_count = filter_queryset_for_user(
            request.user,
            Client.objects.filter(pk__in=client_access),
            "client",
        ).count()
        if allowed_count != len(set(client_access)):
            return False

    return True
