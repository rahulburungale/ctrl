from django.urls import path
from .views import AuditLogAPI, LoginLogAPI

urlpatterns = [
    path("audit-logs/", AuditLogAPI.as_view()),
    path("login-logs/", LoginLogAPI.as_view()),
]
