from rest_framework import serializers
from .models import ProjectTeamMember


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTeamMember
        fields = "__all__"

class ProjectTeamBulkSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    members = serializers.ListField(
        child=serializers.DictField()
    )