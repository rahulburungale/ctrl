from common.views import BaseListCreateAPIView
from access_control.permissions import HasPermission
from .models import Role, Permission
from .serializers import RoleSerializer, PermissionSerializer


class RoleListAPI(BaseListCreateAPIView):
    permission_classes = [HasPermission]
    model = Role
    serializer_class = RoleSerializer
    permission_module = "role"
    module = "ROLE"


class PermissionListAPI(BaseListCreateAPIView):
    permission_classes = [HasPermission]
    model = Permission
    serializer_class = PermissionSerializer
    permission_module = "permission"
    module = "PERMISSION"
