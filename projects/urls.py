from django.urls import path
from .views import (
    ProjectAPI,
    ProjectDetailAPI
)

urlpatterns = [
    path("", ProjectAPI.as_view()),
    path("<int:pk>/", ProjectDetailAPI.as_view()),
]
