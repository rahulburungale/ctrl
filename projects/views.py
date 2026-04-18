from rest_framework.views import APIView
from common.response import APIResponse
from common.pagination import OptionalPagination
from access_control.permissions import HasPermission
from access_control.rbac import filter_queryset_for_user
from clients.models import Client
from departments.models import Department, Division
from .models import Project
from .serializers import ProjectSerializer
from drf_spectacular.utils import extend_schema

class ProjectAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "project"
    module = "PROJECT"

    def get(self, request):
        self.action = "VIEW"

        queryset = Project.objects.filter(is_active=True)
        queryset = filter_queryset_for_user(request.user, queryset, "project")

        paginator = OptionalPagination()
        paginated = paginator.paginate_queryset(queryset, request)

        if paginated:
            return paginator.get_paginated_response(
                ProjectSerializer(paginated, many=True).data
            )

        return APIResponse.success(
            data=ProjectSerializer(queryset, many=True).data
        )

    @extend_schema(request=ProjectSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department_id = serializer.validated_data.get("department_id")
        division_id = serializer.validated_data.get("division_id")
        client_id = serializer.validated_data.get("client_id")
        allowed_department = filter_queryset_for_user(
            request.user,
            Department.objects.filter(pk=department_id),
            "department",
        ).exists()
        allowed_client = filter_queryset_for_user(
            request.user,
            Client.objects.filter(pk=client_id),
            "client",
        ).exists()
        if not allowed_department or not allowed_client:
            return APIResponse.error("Invalid department or client access", 403)
        if division_id:
            allowed_division = filter_queryset_for_user(
                request.user,
                Division.objects.filter(pk=division_id, department_id=department_id),
                "division",
            ).exists()
            if not allowed_division:
                return APIResponse.error("Invalid division access", 403)
        serializer.save(created_by=request.user)

        return APIResponse.success(
            "Project created successfully",
            serializer.data
        )


class ProjectDetailAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "project"
    module = "PROJECT"
    permission_required = {
        "PUT": "project.update",
        "PATCH": "project.restore",
        "DELETE": "project.delete",
    }

    @extend_schema(request=ProjectSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        project = filter_queryset_for_user(
            request.user,
            Project.objects.filter(pk=pk),
            "project",
        ).first()
        if not project:
            return APIResponse.error("Project not found", 404)

        serializer = ProjectSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        department_id = serializer.validated_data.get("department_id", project.department_id)
        division_id = serializer.validated_data.get("division_id", project.division_id)
        client_id = serializer.validated_data.get("client_id", project.client_id)
        allowed_department = filter_queryset_for_user(
            request.user,
            Department.objects.filter(pk=department_id),
            "department",
        ).exists()
        allowed_client = filter_queryset_for_user(
            request.user,
            Client.objects.filter(pk=client_id),
            "client",
        ).exists()
        if not allowed_department or not allowed_client:
            return APIResponse.error("Invalid department or client access", 403)
        if division_id:
            allowed_division = filter_queryset_for_user(
                request.user,
                Division.objects.filter(pk=division_id, department_id=department_id),
                "division",
            ).exists()
            if not allowed_division:
                return APIResponse.error("Invalid division access", 403)
        serializer.save(updated_by=request.user)

        return APIResponse.success("Project updated", serializer.data)

    def delete(self, request, pk):
        self.action = "DELETE"

        project = filter_queryset_for_user(
            request.user,
            Project.objects.filter(pk=pk),
            "project",
        ).first()
        if not project:
            return APIResponse.error("Project not found", 404)

        project.is_active = False
        project.updated_by = request.user
        project.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Project deleted")

    def patch(self, request, pk):
        """ Restore """
        self.action = "RESTORE"

        project = filter_queryset_for_user(
            request.user,
            Project.objects.filter(pk=pk),
            "project",
        ).first()
        if not project:
            return APIResponse.error("Project not found", 404)

        project.is_active = True
        project.updated_by = request.user
        project.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Project restored")
