from django.db import models
from accounts.models import User


class Grade(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "grades"


class Designation(models.Model):
    name = models.CharField(max_length=100)
    grade = models.ForeignKey(Grade, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        db_table = "designations"
