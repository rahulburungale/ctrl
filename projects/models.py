from django.db import models
from accounts.models import User


class Project(models.Model):
    project_name = models.CharField(max_length=255)
    job_no = models.CharField(max_length=100, unique=True)
    department_id = models.BigIntegerField()
    division_id = models.BigIntegerField(null=True, blank=True)
    client_id = models.BigIntegerField()
    status = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        db_table = "projects"
