from django.db import models
from accounts.models import User
from departments.models import Department
from clients.models import Client


class Role(models.Model):
    name = models.CharField(max_length=100)
    # is_superadmin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        db_table = "roles"


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_superadmin = models.BooleanField(default=False)
    class Meta:
        db_table = "user_roles"


class Permission(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        db_table = "permissions"


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permissions = models.JSONField()

    class Meta:
        db_table = "role_permissions"


class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permissions = models.JSONField()

    class Meta:
        db_table = "user_permissions"

class DepartmentAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        db_table = "department_access"


class ClientAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

    class Meta:
        db_table = "client_access"
