from rest_framework import serializers
from .models import Role, Permission


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]
