from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from clients.authentication import ClientJWTAuthentication
from common.response import APIResponse
from projects.models import Project
from clients.serializers import ClientProjectDetailSerializer, ClientListSerializer


class ClientProjectList(APIView):
    authentication_classes = [ClientJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user

        projects = Project.objects.filter(client_id=client.id, is_active=True).order_by("-created_at")

        return APIResponse.success(
            data={
                "client": ClientListSerializer(client).data,
                "projects": ClientProjectDetailSerializer(projects, many=True).data,
            }
        )
