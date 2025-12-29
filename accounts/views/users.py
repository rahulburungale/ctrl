from rest_framework.views import APIView
from access_control.permissions import HasPermission
from accounts.models import User
from accounts.serializers import UserCreateSerializer
from common.response import APIResponse
from common.pagination import OptionalPagination
from drf_spectacular.utils import extend_schema


class UserAPI(APIView):
    permission_classes = [HasPermission]
    module = "USER"

    def get(self, request):
        self.action = "VIEW"

        queryset = User.objects.filter(is_active=True)

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
        serializer.save(created_by=request.user)

        return APIResponse.success(
            message="User created successfully",
            data=serializer.data
        )


class UserDetailAPI(APIView):
    permission_classes = [HasPermission]
    module = "USER"

    @extend_schema(request=UserCreateSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        user = User.objects.filter(pk=pk).first()
        if not user:
            return APIResponse.error("User not found", 404)

        serializer = UserCreateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success(
            message="User updated successfully",
            data=serializer.data
        )
    
    def delete(self, request, pk):
        self.action = "DELETE"

        user = User.objects.filter(pk=pk).first()
        if not user:
            return APIResponse.error("User not found", 404)

        user.is_active = False
        user.save(update_fields=["is_active"])

        return APIResponse.success("User deactivated successfully")

    def patch(self, request, pk):
        """
        Restore user
        """
        self.action = "RESTORE"

        user = User.objects.filter(pk=pk).first()
        if not user:
            return APIResponse.error("User not found", 404)

        user.is_active = True
        user.save(update_fields=["is_active"])

        return APIResponse.success("User restored successfully")
