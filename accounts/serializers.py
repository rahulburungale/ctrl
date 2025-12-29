from rest_framework import serializers
from .models import User
from access_control.models import UserRole, UserPermission
from departments.models import Department
from clients.models import Client


from rest_framework import serializers
from django.db import transaction
from .models import User
from access_control.models import (
    UserRole,
    UserPermission,
    DepartmentAccess,
    ClientAccess,
)


class UserCreateSerializer(serializers.ModelSerializer):
    role_id = serializers.IntegerField(write_only=True)
    permissions = serializers.JSONField(write_only=True)
    department_access = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    client_access = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "employee_code",
            "department_id",
            "designation_id",
            "reporting_to",
            "is_active",
            "password",
            "role_id",
            "permissions",
            "department_access",
            "client_access",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        role_id = validated_data.pop("role_id")
        permissions = validated_data.pop("permissions", {})
        department_access = validated_data.pop("department_access", [])
        client_access = validated_data.pop("client_access", [])
        password = validated_data.pop("password", None)

        with transaction.atomic():
            user = User.objects.create(**validated_data)

            if password:
                user.set_password(password)
                user.save()

            # Assign role
            UserRole.objects.create(
                user=user,
                role_id=role_id
            )

            # User permissions
            UserPermission.objects.create(
                user=user,
                permissions=permissions
            )

            # Department access
            DepartmentAccess.objects.bulk_create([
                DepartmentAccess(user=user, department_id=dept)
                for dept in department_access
            ])

            # Client access
            ClientAccess.objects.bulk_create([
                ClientAccess(user=user, client_id=client)
                for client in client_access
            ])

        return user

    def update(self, instance, validated_data):
        role_id = validated_data.pop("role_id", None)
        permissions = validated_data.pop("permissions", None)
        department_access = validated_data.pop("department_access", None)
        client_access = validated_data.pop("client_access", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if role_id:
            UserRole.objects.update_or_create(
                user=instance,
                defaults={"role_id": role_id}
            )

        if permissions is not None:
            UserPermission.objects.update_or_create(
                user=instance,
                defaults={"permissions": permissions}
            )

        if department_access is not None:
            DepartmentAccess.objects.filter(user=instance).delete()
            DepartmentAccess.objects.bulk_create([
                DepartmentAccess(user=instance, department_id=d)
                for d in department_access
            ])

        if client_access is not None:
            ClientAccess.objects.filter(user=instance).delete()
            ClientAccess.objects.bulk_create([
                ClientAccess(user=instance, client_id=c)
                for c in client_access
            ])

        return instance


class LoginSerializer(serializers.Serializer):
    employee_code = serializers.CharField()
    password = serializers.CharField()


class OTPLoginSerializer(serializers.Serializer):
    employee_code = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()

class UserDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    employee_code = serializers.CharField()
    is_active = serializers.BooleanField()


class UserPermissionResponseSerializer(serializers.Serializer):
    user = UserDetailSerializer()
    roles = serializers.ListField(child=serializers.CharField())
    permissions = serializers.DictField()
    department_access = serializers.ListField(child=serializers.IntegerField())
    client_access = serializers.ListField(child=serializers.IntegerField())