from rest_framework import serializers
from .models import Client
from django.contrib.auth.hashers import check_password


class ClientLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "name", "email", "phone"]

class ClientCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "password",
            "is_active",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        client = Client(**validated_data)
        client.set_password(password)
        client.save()
        return client

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "is_active",
        ]