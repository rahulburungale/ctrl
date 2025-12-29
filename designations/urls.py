from django.urls import path
from .views import DesignationAPI, DesignationDetailAPI

urlpatterns = [
    path("", DesignationAPI.as_view()),
    path("<int:pk>/", DesignationDetailAPI.as_view()),
]
