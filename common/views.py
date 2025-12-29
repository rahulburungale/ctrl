from rest_framework.views import APIView
from rest_framework.response import Response
from access_control.permissions import HasPermission


class BaseListCreateAPIView(APIView):
    model = None
    serializer_class = None
    module = None

    def get(self, request):
        self.action = "VIEW"
        queryset = self.model.objects.all()
        return Response(self.serializer_class(queryset, many=True).data)

    def post(self, request):
        self.action = "ADD"
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(serializer.data)
