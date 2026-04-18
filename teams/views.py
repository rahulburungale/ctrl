from rest_framework.views import APIView
from common.response import APIResponse
from common.pagination import OptionalPagination
from access_control.permissions import HasPermission
from access_control.rbac import filter_queryset_for_user
from projects.models import Project
from .models import ProjectTeamMember
from .serializers import (
    PROJECT_MANAGER_ROLE,
    ProjectTeamBulkSerializer,
    ProjectTeamMemberSerializer,
)
from drf_spectacular.utils import extend_schema


class ProjectTeamMemberAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "project"
    module = "PROJECT"

    def get(self, request):
        self.action = "VIEW"

        project_id = request.GET.get("project_id")
        queryset = ProjectTeamMember.objects.all()

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        queryset = filter_queryset_for_user(request.user, queryset, "team")

        paginator = OptionalPagination()
        paginated = paginator.paginate_queryset(queryset, request)

        if paginated:
            return paginator.get_paginated_response(
                ProjectTeamMemberSerializer(paginated, many=True).data
            )

        return APIResponse.success(
            data=ProjectTeamMemberSerializer(queryset, many=True).data
        )

    @extend_schema(request=ProjectTeamMemberSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = ProjectTeamMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project_id = serializer.validated_data["project_id"]
        allowed_project = filter_queryset_for_user(
            request.user,
            Project.objects.filter(pk=project_id),
            "project",
        ).exists()
        if not allowed_project:
            return APIResponse.error("Project not found", 404)
        serializer.save()

        return APIResponse.success(
            "Team member added",
            serializer.data
        )


class ProjectTeamMemberDetailAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "project"
    module = "PROJECT"
    permission_required = {
        "PUT": "project.update",
        "DELETE": "project.delete",
    }

    @extend_schema(request=ProjectTeamMemberSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        obj = filter_queryset_for_user(
            request.user,
            ProjectTeamMember.objects.filter(pk=pk),
            "team",
        ).first()
        if not obj:
            return APIResponse.error("Team member not found", 404)

        serializer = ProjectTeamMemberSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse.success("Team member updated", serializer.data)

    def delete(self, request, pk):
        self.action = "DELETE"

        obj = filter_queryset_for_user(
            request.user,
            ProjectTeamMember.objects.filter(pk=pk),
            "team",
        ).first()
        if not obj:
            return APIResponse.error("Team member not found", 404)

        obj.delete()
        return APIResponse.success("Team member removed")
    
class ProjectTeamBulkAssignAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "project"
    module = "PROJECT"
    permission_required = {
        "POST": "project.update",
    }

    @extend_schema(request=ProjectTeamBulkSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = ProjectTeamBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = serializer.validated_data["project_id"]
        members = serializer.validated_data["members"]
        allowed_project = filter_queryset_for_user(
            request.user,
            Project.objects.filter(pk=project_id),
            "project",
        ).exists()
        if not allowed_project:
            return APIResponse.error("Project not found", 404)

        created = []
        final_roles = {
            member.user_id: member.role
            for member in ProjectTeamMember.objects.filter(project_id=project_id)
        }
        for member in members:
            final_roles[member["user_id"]] = member["role"]

        final_manager_count = sum(
            1
            for role in final_roles.values()
            if role.strip().lower() == PROJECT_MANAGER_ROLE.lower()
        )
        if final_manager_count > 1:
            return APIResponse.error(
                "Only one Project Manager can be assigned to a project",
                status=400,
            )

        for member in members:
            obj, _ = ProjectTeamMember.objects.update_or_create(
                project_id=project_id,
                user_id=member["user_id"],
                defaults={
                    "role": member["role"],
                    "reporting_to_id": member.get("reporting_to"),
                }
            )
            created.append(obj)

        return APIResponse.success(
            "Team members assigned successfully",
            data={"count": len(created)}
        )
