from rest_framework import serializers
from .models import Client
from django.contrib.auth.hashers import check_password
from departments.models import Department, Division
from teams.models import ProjectTeamMember
from teams.serializers import PROJECT_MANAGER_ROLE, TEAM_LEADER_ROLE, ProjectTeamMemberSerializer


class ClientLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "email", "phone"]

class ClientCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "password",
            "is_active",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = [
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        client = Client(**validated_data)
        client.set_password(password)
        client.save()
        return client

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "is_active",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = [
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class ClientProjectDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    project_name = serializers.CharField()
    job_no = serializers.CharField()
    department_id = serializers.IntegerField()
    department_name = serializers.SerializerMethodField()
    division_id = serializers.IntegerField(allow_null=True)
    division_name = serializers.SerializerMethodField()
    client_id = serializers.IntegerField()
    status = serializers.CharField()
    project_progress = serializers.SerializerMethodField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    project_manager = serializers.SerializerMethodField()
    team_leaders = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    def get_department_name(self, obj):
        department = Department.objects.filter(pk=obj.department_id).first()
        return department.name if department else None

    def get_division_name(self, obj):
        division = Division.objects.filter(pk=obj.division_id).first()
        return division.name if division else None

    def get_project_progress(self, obj):
        return {
            "status": obj.status,
            "start_date": obj.start_date,
            "end_date": obj.end_date,
        }

    def get_project_manager(self, obj):
        manager = (
            ProjectTeamMember.objects
            .filter(project_id=obj.id, role__iexact=PROJECT_MANAGER_ROLE)
            .select_related("user", "reporting_to")
            .first()
        )
        return ProjectTeamMemberSerializer(manager).data if manager else None

    def get_team_leaders(self, obj):
        team_leaders = (
            ProjectTeamMember.objects
            .filter(project_id=obj.id, role__iexact=TEAM_LEADER_ROLE)
            .select_related("user", "reporting_to")
        )
        return ProjectTeamMemberSerializer(team_leaders, many=True).data

    def get_team(self, obj):
        team = (
            ProjectTeamMember.objects
            .filter(project_id=obj.id)
            .select_related("user", "reporting_to")
            .order_by("role", "user__full_name")
        )
        return ProjectTeamMemberSerializer(team, many=True).data
