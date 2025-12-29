from rest_framework.views import APIView
from access_control.permissions import HasPermission
from common.response import APIResponse
from common.pagination import OptionalPagination
from .models import Department
from .serializers import DepartmentSerializer
from drf_spectacular.utils import extend_schema

class DepartmentAPI(APIView):
    permission_classes = [HasPermission]
    module = "DEPARTMENT"

    def get(self, request):
        self.action = "VIEW"
        queryset  = Department.objects.filter(is_active=True)

        paginator = OptionalPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)

        if paginated_data is not None:
            serializer = DepartmentSerializer(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        return APIResponse.success(DepartmentSerializer(queryset, many=True).data)

    @extend_schema(request=DepartmentSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return APIResponse.success("Department created", serializer.data)


class DepartmentDetailAPI(APIView):
    permission_classes = [HasPermission]
    module = "DEPARTMENT"

    @extend_schema(request=DepartmentSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        dept = Department.objects.filter(pk=pk).first()
        if not dept:
            return APIResponse.error("Department not found", 404)

        serializer = DepartmentSerializer(dept, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success("Department updated", serializer.data)

    def delete(self, request, pk):
        self.action = "DELETE"

        dept = Department.objects.filter(pk=pk).first()
        if not dept:
            return APIResponse.error("Department not found", 404)

        dept.is_active = False
        dept.save(update_fields=["is_active"])

        return APIResponse.success("Department deleted")
    
    def patch(self, request, pk):
        self.action = "RESTORE"

        dept = Department.objects.filter(pk=pk).first()
        if not dept:
            return APIResponse.error("Department not found", 404)

        dept.is_active = True
        dept.save(update_fields=["is_active"])

        return APIResponse.success("Department restored")
