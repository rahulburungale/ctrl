from django.db import models
from accounts.models import User
from django.contrib.auth.hashers import make_password, check_password


class Client(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    password = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="+")

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    class Meta:
        db_table = "clients"