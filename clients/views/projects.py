from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from clients.authentication import ClientJWTAuthentication
from common.response import APIResponse
from projects.models import Project
from projects.serializers import ProjectSerializer


class ClientProjectList(APIView):
    authentication_classes = [ClientJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user

        projects = Project.objects.filter(client_id=client.id)

        return APIResponse.success(
            data=ProjectSerializer(projects, many=True).data
        )
