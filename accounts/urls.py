from django.urls import path
from .views.auth import LoginPassword, LoginOTP, VerifyOTP
from .views.users import UserAPI, UserDetailAPI
from .views.user_profile import (
    ProfileUpdateAPI,
    ResetPasswordAPI,
    UpdatePasswordAPI,
    UserProfileAPI,
)

urlpatterns = [
    path("auth/login/", LoginPassword.as_view()),
    path("auth/login/otp/", LoginOTP.as_view()),
    path("auth/me/", UserProfileAPI.as_view()),
    path("auth/me/profile/", ProfileUpdateAPI.as_view()),
    path("auth/me/update-password/", UpdatePasswordAPI.as_view()),
    path("auth/me/reset-password/", ResetPasswordAPI.as_view()),
    path("auth/login/verify-otp/", VerifyOTP.as_view()),
    path("users/", UserAPI.as_view()),
    path("users/<int:pk>/", UserDetailAPI.as_view()),
]
