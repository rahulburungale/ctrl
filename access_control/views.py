from common.views import BaseListCreateAPIView
from .models import Role, Permission
from .serializers import RoleSerializer, PermissionSerializer


class RoleListAPI(BaseListCreateAPIView):
    model = Role
    serializer_class = RoleSerializer
    module = "ROLE"


class PermissionListAPI(BaseListCreateAPIView):
    model = Permission
    serializer_class = PermissionSerializer
    module = "PERMISSION"
