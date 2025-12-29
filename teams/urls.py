from django.urls import path
from .views import (
    ProjectTeamMemberAPI,
    ProjectTeamMemberDetailAPI,
    ProjectTeamBulkAssignAPI
)

urlpatterns = [
    path("team-members/", ProjectTeamMemberAPI.as_view()),
    path("team-members/<int:pk>/", ProjectTeamMemberDetailAPI.as_view()),
    path("team-members/bulk/", ProjectTeamBulkAssignAPI.as_view()),
]
