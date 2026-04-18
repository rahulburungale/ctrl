from rest_framework.views import APIView
from access_control.permissions import HasPermission
from access_control.rbac import filter_queryset_for_user
from .models import AuditLog, LoginLog
from .serializers import AuditLogSerializer, LoginLogSerializer
from common.response import APIResponse


class AuditLogAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "audit"
    module = "AUDIT"

    def get(self, request):
        self.action = "VIEW"

        entity_id = request.GET.get("entity_id")

        logs = AuditLog.objects.all().order_by("-created_at")
        logs = filter_queryset_for_user(request.user, logs, "audit")

        if entity_id:
            logs = logs.filter(entity_id=entity_id)

        return APIResponse.success(
            data=AuditLogSerializer(logs, many=True).data
        )


class LoginLogAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "login_log"
    module = "LOGIN_LOG"

    def get(self, request):
        self.action = "VIEW"

        logs = LoginLog.objects.all().order_by("-login_time")
        logs = filter_queryset_for_user(request.user, logs, "audit")

        return APIResponse.success(
            data=LoginLogSerializer(logs, many=True).data
        )
