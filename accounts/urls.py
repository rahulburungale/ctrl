from django.urls import path
from .views.auth import LoginPassword, LoginOTP, VerifyOTP
from .views.users import UserAPI, UserDetailAPI
from .views.user_profile import UserProfileAPI

urlpatterns = [
    path("auth/login/", LoginPassword.as_view()),
    path("auth/login/otp/", LoginOTP.as_view()),
    path("auth/me/", UserProfileAPI.as_view()),
    path("auth/login/verify-otp/", VerifyOTP.as_view()),
    path("users/", UserAPI.as_view()),
    path("users/<int:pk>/", UserDetailAPI.as_view()),
]
