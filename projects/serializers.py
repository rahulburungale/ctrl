from rest_framework import serializers
from clients.models import Client
from departments.models import Department, Division
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    division_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "project_name",
            "job_no",
            "department_id",
            "department_name",
            "division_id",
            "division_name",
            "client_id",
            "client_name",
            "status",
            "start_date",
            "end_date",
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

    def get_client_name(self, obj):
        client = Client.objects.filter(pk=obj.client_id).first()
        return client.name if client else None

    def get_department_name(self, obj):
        department = Department.objects.filter(pk=obj.department_id).first()
        return department.name if department else None

    def get_division_name(self, obj):
        division = Division.objects.filter(pk=obj.division_id).first()
        return division.name if division else None
