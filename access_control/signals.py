from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from access_control.models import DivisionAccess, RolePermission, UserPermission, UserRole
from access_control.rbac import clear_user_rbac_cache


def _clear_role_users(role_id):
    user_ids = UserRole.objects.filter(role_id=role_id).values_list("user_id", flat=True)
    for user_id in user_ids:
        clear_user_rbac_cache(user_id)


@receiver([post_save, post_delete], sender=UserRole)
def clear_user_role_cache(sender, instance, **kwargs):
    clear_user_rbac_cache(instance.user_id)


@receiver([post_save, post_delete], sender=UserPermission)
def clear_user_permission_cache(sender, instance, **kwargs):
    clear_user_rbac_cache(instance.user_id)


@receiver([post_save, post_delete], sender=DivisionAccess)
def clear_division_access_cache(sender, instance, **kwargs):
    clear_user_rbac_cache(instance.user_id)


@receiver([post_save, post_delete], sender=RolePermission)
def clear_role_permission_cache(sender, instance, **kwargs):
    _clear_role_users(instance.role_id)
