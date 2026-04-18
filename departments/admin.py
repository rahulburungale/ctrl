from django.contrib import admin
from .models import Department, Division


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "department", "is_active")
    search_fields = ("name", "department__name")
    list_filter = ("department", "is_active")
