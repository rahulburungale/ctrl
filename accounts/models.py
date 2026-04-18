from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, employee_code, password=None, **extra_fields):
        user = self.model(employee_code=employee_code, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    employee_code = models.CharField(max_length=100, unique=True)

    department_id = models.BigIntegerField(null=True)
    division_id = models.BigIntegerField(null=True)
    designation_id = models.BigIntegerField(null=True)

    reporting_to = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("self", null=True, on_delete=models.SET_NULL, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey("self", null=True, on_delete=models.SET_NULL, related_name="+")

    USERNAME_FIELD = "employee_code"

    objects = UserManager()

    class Meta:
        db_table = "users"


class OTPRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_requests"
