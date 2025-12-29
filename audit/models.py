from django.db import models
from accounts.models import User


class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    entity_id = models.BigIntegerField(null=True, blank=True)
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"


class LoginLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    identifier = models.CharField(max_length=150, null=True, blank=True)
    ip_address = models.CharField(max_length=100, null=True, blank=True)
    device = models.TextField(null=True, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    is_success = models.BooleanField(default=True)

    class Meta:
        db_table = "login_logs"
