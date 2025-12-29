from django.db import models
from accounts.models import User


class ProjectTeamMember(models.Model):
    project_id = models.BigIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    reporting_to = models.ForeignKey(User, null=True, blank=True, related_name="+", on_delete=models.SET_NULL)

    class Meta:
        db_table = "project_team_members"
