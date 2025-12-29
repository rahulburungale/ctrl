from rest_framework.views import APIView
from access_control.permissions import HasPermission
from common.response import APIResponse
from .models import Designation
from .serializers import DesignationSerializer
from common.pagination import OptionalPagination
from drf_spectacular.utils import extend_schema


class DesignationAPI(APIView):
    permission_classes = [HasPermission]
    module = "DESIGNATION"

    def get(self, request):
        self.action = "VIEW"
        queryset = Designation.objects.filter(is_active=True)

        paginator = OptionalPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)

        if paginated_data:
            return paginator.get_paginated_response(
                DesignationSerializer(paginated_data, many=True).data
            )
        
        return APIResponse.success(DesignationSerializer(queryset, many=True).data)

    @extend_schema(request=DesignationSerializer)
    def post(self, request):
        self.action = "ADD"

        serializer = DesignationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

        return APIResponse.success("Designation created", serializer.data)


class DesignationDetailAPI(APIView):
    permission_classes = [HasPermission]
    module = "DESIGNATION"

    @extend_schema(request=DesignationSerializer)
    def put(self, request, pk):
        self.action = "EDIT"

        obj = Designation.objects.filter(pk=pk).first()
        if not obj:
            return APIResponse.error("Designation not found", 404)

        serializer = DesignationSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        return APIResponse.success("Designation updated", serializer.data)

    def delete(self, request, pk):
        self.action = "DELETE"

        obj = Designation.objects.filter(pk=pk).first()
        if not obj:
            return APIResponse.error("Designation not found", 404)

        obj.is_active = False
        obj.save(update_fields=["is_active"])

        return APIResponse.success("Designation deleted")

    def patch(self, request, pk):
        self.action = "RESTORE"

        obj = Designation.objects.filter(pk=pk).first()
        if not obj:
            return APIResponse.error("Designation not found", 404)

        obj.is_active = True
        obj.save(update_fields=["is_active"])

        return APIResponse.success("Designation restored")
