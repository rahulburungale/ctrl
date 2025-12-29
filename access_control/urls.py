from django.urls import path
from .views import RoleListAPI, PermissionListAPI

urlpatterns = [
    path("roles/", RoleListAPI.as_view()),
    path("permissions/", PermissionListAPI.as_view()),
]
