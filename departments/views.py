from rest_framework.views import APIView
from access_control.permissions import HasPermission
from access_control.rbac import filter_queryset_for_user
from common.response import APIResponse
from common.pagination import OptionalPagination
from .models import Department, Division
from .serializers import DepartmentSerializer, DivisionSerializer
from drf_spectacular.utils import extend_schema

class DepartmentAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "department"
    module = "DEPARTMENT"

    def get(self, request):
        self.action = "VIEW"
        queryset  = Department.objects.filter(is_active=True)
        queryset = filter_queryset_for_user(request.user, queryset, "department")

        paginator = OptionalPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)

        if paginated_data is not None:
            serializer = DepartmentSerializer(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        return APIResponse.success(data=DepartmentSerializer(queryset, many=True).data)

    @extend_schema(request=DepartmentSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return APIResponse.success("Department created", serializer.data)


class DepartmentDetailAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "department"
    module = "DEPARTMENT"
    permission_required = {
        "PUT": "department.update",
        "PATCH": "department.restore",
        "DELETE": "department.delete",
    }

    @extend_schema(request=DepartmentSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        dept = filter_queryset_for_user(
            request.user,
            Department.objects.filter(pk=pk),
            "department",
        ).first()
        if not dept:
            return APIResponse.error("Department not found", 404)

        serializer = DepartmentSerializer(dept, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success("Department updated", serializer.data)

    def delete(self, request, pk):
        self.action = "DELETE"

        dept = filter_queryset_for_user(
            request.user,
            Department.objects.filter(pk=pk),
            "department",
        ).first()
        if not dept:
            return APIResponse.error("Department not found", 404)

        dept.is_active = False
        dept.updated_by = request.user
        dept.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Department deleted")
    
    def patch(self, request, pk):
        self.action = "RESTORE"

        dept = filter_queryset_for_user(
            request.user,
            Department.objects.filter(pk=pk),
            "department",
        ).first()
        if not dept:
            return APIResponse.error("Department not found", 404)

        dept.is_active = True
        dept.updated_by = request.user
        dept.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Department restored")


class DivisionAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "division"
    module = "DIVISION"

    def get(self, request):
        queryset = Division.objects.filter(is_active=True).select_related("department")
        queryset = filter_queryset_for_user(request.user, queryset, "division")

        department_id = request.GET.get("department_id")
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        paginator = OptionalPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)

        if paginated_data is not None:
            serializer = DivisionSerializer(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)

        return APIResponse.success(data=DivisionSerializer(queryset, many=True).data)

    @extend_schema(request=DivisionSerializer)
    def post(self, request):
        serializer = DivisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return APIResponse.success("Division created", serializer.data)


class DivisionDetailAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "division"
    module = "DIVISION"
    permission_required = {
        "PUT": "division.update",
        "PATCH": "division.restore",
        "DELETE": "division.delete",
    }

    @extend_schema(request=DivisionSerializer)
    def put(self, request, pk):
        obj = filter_queryset_for_user(
            request.user,
            Division.objects.filter(pk=pk),
            "division",
        ).first()
        if not obj:
            return APIResponse.error("Division not found", 404)

        serializer = DivisionSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success("Division updated", serializer.data)

    def delete(self, request, pk):
        obj = filter_queryset_for_user(
            request.user,
            Division.objects.filter(pk=pk),
            "division",
        ).first()
        if not obj:
            return APIResponse.error("Division not found", 404)

        obj.is_active = False
        obj.updated_by = request.user
        obj.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Division deleted")

    def patch(self, request, pk):
        obj = filter_queryset_for_user(
            request.user,
            Division.objects.filter(pk=pk),
            "division",
        ).first()
        if not obj:
            return APIResponse.error("Division not found", 404)

        obj.is_active = True
        obj.updated_by = request.user
        obj.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Division restored")
