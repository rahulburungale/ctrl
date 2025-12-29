from django.urls import path
from .views import DepartmentAPI, DepartmentDetailAPI

urlpatterns = [
    path("", DepartmentAPI.as_view()),
    path("<int:pk>/", DepartmentDetailAPI.as_view()),
]
