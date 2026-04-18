from rest_framework import serializers
from .models import Designation, Grade


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = "__all__"


class DesignationSerializer(serializers.ModelSerializer):
    grade_id = serializers.IntegerField(source="grade.id", read_only=True)
    grade_name = serializers.CharField(source="grade.name", read_only=True)

    class Meta:
        model = Designation
        fields = [
            "id",
            "name",
            "grade",
            "grade_id",
            "grade_name",
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
