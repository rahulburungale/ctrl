import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from clients.models import Client
from clients.serializers import ClientLoginSerializer, ClientSerializer
from common.response import APIResponse
from audit.services import log_login
from drf_spectacular.utils import extend_schema

class ClientLogin(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=ClientLoginSerializer)
    def post(self, request):
        serializer = ClientLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        client = Client.objects.filter(email=email, is_active=True).first()

        if not client or not client.check_password(password):
            return APIResponse.error("Invalid credentials", 401)

        payload = {
            "client_id": client.id,
            "email": client.email,
            "type": "client",
            "exp": datetime.utcnow() + timedelta(hours=12),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return APIResponse.success(
            "Login successful",
            {
                "access": token,
                "client": {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                },
            },
        )
