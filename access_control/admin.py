from django.contrib import admin
from .models import (
    ClientAccess,
    DepartmentAccess,
    DivisionAccess,
    Permission,
    Role,
    RolePermission,
    UserPermission,
    UserRole,
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "is_superadmin")
    search_fields = ("user__employee_code", "user__full_name", "role__name")
    list_filter = ("is_superadmin", "role")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "role")
    search_fields = ("role__name",)


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__employee_code", "user__full_name")


@admin.register(DepartmentAccess)
class DepartmentAccessAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department")
    search_fields = ("user__employee_code", "user__full_name", "department__name")


@admin.register(DivisionAccess)
class DivisionAccessAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "division")
    search_fields = ("user__employee_code", "user__full_name", "division__name")
    list_filter = ("division__department", "division")


@admin.register(ClientAccess)
class ClientAccessAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "client")
    search_fields = ("user__employee_code", "user__full_name", "client__name")
