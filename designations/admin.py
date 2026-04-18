from django.contrib import admin
from .models import Designation, Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "grade", "is_active")
    search_fields = ("name", "grade__name")
    list_filter = ("grade", "is_active")
