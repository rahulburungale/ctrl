from django.urls import path
from .views import DepartmentAPI, DepartmentDetailAPI, DivisionAPI, DivisionDetailAPI

urlpatterns = [
    path("", DepartmentAPI.as_view()),
    path("<int:pk>/", DepartmentDetailAPI.as_view()),
    path("divisions/", DivisionAPI.as_view()),
    path("divisions/<int:pk>/", DivisionDetailAPI.as_view()),
]
