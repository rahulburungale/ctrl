from rest_framework.views import APIView
from access_control.permissions import HasPermission
from access_control.rbac import filter_queryset_for_user
from common.response import APIResponse
from common.pagination import OptionalPagination
from clients.models import Client
from clients.serializers import ClientCreateSerializer, ClientListSerializer
from drf_spectacular.utils import extend_schema

class ClientAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "client"
    module = "CLIENT"

    def get(self, request):
        self.action = "VIEW"
        queryset  = Client.objects.filter(is_active=True)
        queryset = filter_queryset_for_user(request.user, queryset, "client")

        paginator = OptionalPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)

        if paginated_data is not None:
            serializer = ClientListSerializer(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        return APIResponse.success(
            data=ClientListSerializer(queryset , many=True).data
        )

    @extend_schema(request=ClientCreateSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = ClientCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return APIResponse.success(
            "Client created successfully",
            serializer.data
        )


class ClientDetailAPI(APIView):
    permission_classes = [HasPermission]
    permission_module = "client"
    module = "CLIENT"
    permission_required = {
        "PUT": "client.update",
        "PATCH": "client.restore",
        "DELETE": "client.delete",
    }

    @extend_schema(request=ClientCreateSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        client = filter_queryset_for_user(
            request.user,
            Client.objects.filter(pk=pk),
            "client",
        ).first()
        if not client:
            return APIResponse.error("Client not found", 404)

        serializer = ClientCreateSerializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success(
            "Client updated successfully",
            serializer.data
        )

    def delete(self, request, pk):
        self.action = "DELETE"

        client = filter_queryset_for_user(
            request.user,
            Client.objects.filter(pk=pk),
            "client",
        ).first()
        if not client:
            return APIResponse.error("Client not found", 404)

        client.is_active = False
        client.updated_by = request.user
        client.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Client deactivated successfully")

    def patch(self, request, pk):
        """
        Restore client
        """
        self.action = "RESTORE"

        client = filter_queryset_for_user(
            request.user,
            Client.objects.filter(pk=pk),
            "client",
        ).first()
        if not client:
            return APIResponse.error("Client not found", 404)

        client.is_active = True
        client.updated_by = request.user
        client.save(update_fields=["is_active", "updated_by", "updated_at"])

        return APIResponse.success("Client restored successfully")
