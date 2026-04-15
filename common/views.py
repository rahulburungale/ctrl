from rest_framework.views import APIView
from rest_framework.response import Response
from access_control.permissions import HasPermission
from .response import APIResponse
from .pagination import OptionalPagination


class BaseListCreateAPIView(APIView):
    model = None
    serializer_class = None
    module = None

    def dispatch(self, request, *args, **kwargs):
        # Set action based on HTTP method for permission checking
        if request.method == 'GET':
            self.action = "VIEW"
        elif request.method == 'POST':
            self.action = "ADD"
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        queryset = self.model.objects.filter(is_active=True)
        
        paginator = OptionalPagination()
        paginated_data = paginator.paginate_queryset(queryset, request)

        if paginated_data is not None:
            serializer = self.serializer_class(paginated_data, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        return APIResponse.success(
            data=self.serializer_class(queryset, many=True).data
        )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return APIResponse.success(
            message="Created successfully",
            data=serializer.data
        )
