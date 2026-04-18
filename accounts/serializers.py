from rest_framework import serializers
from django.contrib.auth import password_validation
from .models import User
from access_control.models import UserRole, UserPermission
from departments.models import Department, Division
from designations.models import Designation
from clients.models import Client


from rest_framework import serializers
from django.db import transaction
from .models import User
from access_control.models import (
    UserRole,
    UserPermission,
    DepartmentAccess,
    DivisionAccess,
    ClientAccess,
)


class UserCreateSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    division_name = serializers.SerializerMethodField()
    designation_name = serializers.SerializerMethodField()
    role_id = serializers.IntegerField(write_only=True)
    permissions = serializers.JSONField(write_only=True)
    department_access = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    division_access = serializers.ListField(
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
            "department_name",
            "division_id",
            "division_name",
            "designation_id",
            "designation_name",
            "reporting_to",
            "is_active",
            "password",
            "role_id",
            "permissions",
            "department_access",
            "division_access",
            "client_access",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "created_by": {"read_only": True},
            "updated_by": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def get_department_name(self, obj):
        department = Department.objects.filter(pk=obj.department_id).first()
        return department.name if department else None

    def get_division_name(self, obj):
        division = Division.objects.filter(pk=obj.division_id).first()
        return division.name if division else None

    def get_designation_name(self, obj):
        designation = Designation.objects.filter(pk=obj.designation_id).first()
        return designation.name if designation else None

    def create(self, validated_data):
        role_id = validated_data.pop("role_id")
        permissions = validated_data.pop("permissions", {})
        department_access = validated_data.pop("department_access", [])
        division_access = validated_data.pop("division_access", [])
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

            DivisionAccess.objects.bulk_create([
                DivisionAccess(user=user, division_id=division)
                for division in division_access
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
        division_access = validated_data.pop("division_access", None)
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

        if division_access is not None:
            DivisionAccess.objects.filter(user=instance).delete()
            DivisionAccess.objects.bulk_create([
                DivisionAccess(user=instance, division_id=d)
                for d in division_access
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


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
        ]


class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Password confirmation does not match."
            })
        password_validation.validate_password(attrs["new_password"], self.context["request"].user)
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Password confirmation does not match."
            })
        password_validation.validate_password(attrs["new_password"], self.context["request"].user)
        return attrs


class UserDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    employee_code = serializers.CharField()
    department_id = serializers.IntegerField(required=False, allow_null=True)
    department_name = serializers.CharField(required=False, allow_null=True)
    division_id = serializers.IntegerField(required=False, allow_null=True)
    division_name = serializers.CharField(required=False, allow_null=True)
    designation_id = serializers.IntegerField(required=False, allow_null=True)
    designation_name = serializers.CharField(required=False, allow_null=True)
    is_active = serializers.BooleanField()


class UserPermissionResponseSerializer(serializers.Serializer):
    user = UserDetailSerializer()
    roles = serializers.ListField(child=serializers.CharField())
    permissions = serializers.DictField()
    department_access = serializers.ListField(child=serializers.IntegerField())
    division_access = serializers.ListField(child=serializers.IntegerField())
    client_access = serializers.ListField(child=serializers.IntegerField())
    is_superadmin = serializers.BooleanField()
