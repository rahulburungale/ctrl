import jwt
from django.conf import settings
from datetime import datetime, timedelta


def generate_client_token(client):
    payload = {
        "client_id": client.id,
        "email": client.email,
        "type": "client",
        "exp": datetime.utcnow() + timedelta(hours=12),
        "iat": datetime.utcnow()
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
