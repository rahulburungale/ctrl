from rest_framework import serializers
from .models import AuditLog, LoginLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class LoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginLog
        fields = "__all__"
