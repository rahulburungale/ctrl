from rest_framework.views import APIView
from access_control.permissions import HasPermission
from common.response import APIResponse
from common.pagination import OptionalPagination
from clients.models import Client
from clients.serializers import ClientCreateSerializer, ClientListSerializer
from drf_spectacular.utils import extend_schema

class ClientAPI(APIView):
    permission_classes = [HasPermission]
    module = "CLIENT"

    def get(self, request):
        self.action = "VIEW"
        queryset  = Client.objects.filter(is_active=True)

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
        serializer.save()

        return APIResponse.success(
            "Client created successfully",
            serializer.data
        )


class ClientDetailAPI(APIView):
    permission_classes = [HasPermission]
    module = "CLIENT"

    @extend_schema(request=ClientCreateSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        client = Client.objects.filter(pk=pk).first()
        if not client:
            return APIResponse.error("Client not found", 404)

        serializer = ClientCreateSerializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse.success(
            "Client updated successfully",
            serializer.data
        )

    def delete(self, request, pk):
        self.action = "DELETE"

        client = Client.objects.filter(pk=pk).first()
        if not client:
            return APIResponse.error("Client not found", 404)

        client.is_active = False
        client.save(update_fields=["is_active"])

        return APIResponse.success("Client deactivated successfully")

    def patch(self, request, pk):
        """
        Restore client
        """
        self.action = "RESTORE"

        client = Client.objects.filter(pk=pk).first()
        if not client:
            return APIResponse.error("Client not found", 404)

        client.is_active = True
        client.save(update_fields=["is_active"])

        return APIResponse.success("Client restored successfully")
