from rest_framework import serializers
from .models import ProjectTeamMember

PROJECT_MANAGER_ROLE = "Project Manager"
TEAM_LEADER_ROLE = "Team Leader"


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    reporting_to_name = serializers.CharField(source="reporting_to.full_name", read_only=True)

    class Meta:
        model = ProjectTeamMember
        fields = [
            "id",
            "project_id",
            "user",
            "user_name",
            "role",
            "reporting_to",
            "reporting_to_name",
        ]

    def validate(self, attrs):
        project_id = attrs.get("project_id", getattr(self.instance, "project_id", None))
        role = attrs.get("role", getattr(self.instance, "role", None))
        user = attrs.get("user", getattr(self.instance, "user", None))

        if role and role.strip().lower() == PROJECT_MANAGER_ROLE.lower():
            existing = ProjectTeamMember.objects.filter(
                project_id=project_id,
                role__iexact=PROJECT_MANAGER_ROLE,
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    "role": "Only one Project Manager can be assigned to a project."
                })

        if project_id and user:
            duplicate = ProjectTeamMember.objects.filter(project_id=project_id, user=user)
            if self.instance:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError({
                    "user": "This user is already assigned to this project."
                })

        return attrs

class ProjectTeamBulkSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    members = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_members(self, value):
        if not value:
            raise serializers.ValidationError("At least one team member is required.")

        seen_users = set()
        manager_count = 0
        for index, member in enumerate(value):
            if not member.get("user_id"):
                raise serializers.ValidationError({
                    index: "user_id is required."
                })
            if not member.get("role"):
                raise serializers.ValidationError({
                    index: "role is required."
                })

            user_id = member["user_id"]
            if user_id in seen_users:
                raise serializers.ValidationError({
                    index: "Duplicate user_id in the same assignment request."
                })
            seen_users.add(user_id)

            if member["role"].strip().lower() == PROJECT_MANAGER_ROLE.lower():
                manager_count += 1

        if manager_count > 1:
            raise serializers.ValidationError(
                "Only one Project Manager can be assigned in a request."
            )

        return value
