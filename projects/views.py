from rest_framework.views import APIView
from common.response import APIResponse
from common.pagination import OptionalPagination
from access_control.permissions import HasPermission
from .models import Project
from .serializers import ProjectSerializer
from drf_spectacular.utils import extend_schema

class ProjectAPI(APIView):
    permission_classes = [HasPermission]
    module = "PROJECT"

    def get(self, request):
        self.action = "VIEW"

        queryset = Project.objects.filter(is_active=True)

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
        serializer.save(created_by=request.user)

        return APIResponse.success(
            "Project created successfully",
            serializer.data
        )


class ProjectDetailAPI(APIView):
    permission_classes = [HasPermission]
    module = "PROJECT"

    @extend_schema(request=ProjectSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        project = Project.objects.filter(pk=pk).first()
        if not project:
            return APIResponse.error("Project not found", 404)

        serializer = ProjectSerializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success("Project updated", serializer.data)

    def delete(self, request, pk):
        self.action = "DELETE"

        project = Project.objects.filter(pk=pk).first()
        if not project:
            return APIResponse.error("Project not found", 404)

        project.is_active = False
        project.save(update_fields=["is_active"])

        return APIResponse.success("Project deleted")

    def patch(self, request, pk):
        """ Restore """
        self.action = "RESTORE"

        project = Project.objects.filter(pk=pk).first()
        if not project:
            return APIResponse.error("Project not found", 404)

        project.is_active = True
        project.save(update_fields=["is_active"])

        return APIResponse.success("Project restored")
