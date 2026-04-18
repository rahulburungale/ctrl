from rest_framework import serializers
from .models import Department, Division


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class DivisionSerializer(serializers.ModelSerializer):
    department_id = serializers.IntegerField(source="department.id", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Division
        fields = [
            "id",
            "department",
            "department_id",
            "department_name",
            "name",
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
