from .models import AuditLog, LoginLog


def log_action(user, module, action, metadata=None, entity_id=None):
    AuditLog.objects.create(
        user=user,
        module=module,
        action=action,
        entity_id=entity_id,
        metadata=metadata or {}
    )

def log_login(user=None, identifier=None, ip=None, device=None, success=False):
    LoginLog.objects.create(
        user=user,
        identifier=identifier,
        ip_address=ip,
        device=device,
        is_success=success
    )
