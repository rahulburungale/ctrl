from django.urls import path
from .views.auth import ClientLogin
from .views.projects import ClientProjectList
from .views.clients import ClientAPI, ClientDetailAPI

urlpatterns = [
    path("", ClientAPI.as_view()),
    path("<int:pk>/", ClientDetailAPI.as_view()),
    path("login/", ClientLogin.as_view()),
    path("projects/", ClientProjectList.as_view()),
]
