from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from django.conf import settings
from drf_spectacular.utils import extend_schema
from accounts.models import User, OTPRequest
from accounts.serializers import LoginSerializer, OTPLoginSerializer, VerifyOTPSerializer
from common.response import APIResponse
from audit.services import log_login
import random

class LoginPassword(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_code = serializer.validated_data["employee_code"]
        password = serializer.validated_data["password"]

        user = authenticate(
            employee_code=employee_code,
            password=password
        )

        if not user:
            log_login(
                user=None,
                identifier=employee_code,
                ip=request.META.get("REMOTE_ADDR"),
                device=request.META.get("HTTP_USER_AGENT"),
                success=False
            )
            return APIResponse.error("Invalid credentials", 401)

        refresh = RefreshToken.for_user(user)

        log_login(
            user=user,
            identifier=employee_code,
            ip=request.META.get("REMOTE_ADDR"),
            device=request.META.get("HTTP_USER_AGENT"),
            success=True
        )

        return APIResponse.success(
            "Login successful",
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        )
    

class LoginOTP(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=OTPLoginSerializer)
    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee_code = serializer.validated_data["employee_code"]

        user = User.objects.filter(employee_code=employee_code, is_active=True).first()

        if not user:
            log_login(
                user=None,
                identifier=employee_code,
                ip=request.META.get("REMOTE_ADDR"),
                device=request.META.get("HTTP_USER_AGENT"),
                success=False
            )
            return APIResponse.error("User not found", 404)

        otp = str(random.randint(100000, 999999))
        OTPRequest.objects.create(user=user, otp=otp)

        data = {"otp": otp} if settings.DEBUG else None
        return APIResponse.success("OTP sent", data)
    

class VerifyOTP(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=VerifyOTPSerializer)
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = serializer.validated_data["otp"]

        record = OTPRequest.objects.filter(
            otp=otp,
            is_used=False,
            user__is_active=True,
        ).first()

        if not record:
            log_login(
                user=None,
                identifier="OTP",
                ip=request.META.get("REMOTE_ADDR"),
                device=request.META.get("HTTP_USER_AGENT"),
                success=False
            )
            return APIResponse.error("Invalid OTP", 400)

        record.is_used = True
        record.save()

        refresh = RefreshToken.for_user(record.user)

        log_login(
            user=record.user,
            identifier=record.user.employee_code,
            ip=request.META.get("REMOTE_ADDR"),
            device=request.META.get("HTTP_USER_AGENT"),
            success=True
        )

        return APIResponse.success(
            "OTP verified",
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        )
