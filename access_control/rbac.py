import logging

from django.core.cache import cache
from django.db.models import Q

logger = logging.getLogger(__name__)

LEGACY_ACTION_MAP = {
    "ADD": "create",
    "CREATE": "create",
    "VIEW": "view",
    "READ": "view",
    "EDIT": "update",
    "UPDATE": "update",
    "DELETE": "delete",
    "RESTORE": "restore",
    "SUBMIT": "submit",
}

HTTP_ACTION_MAP = {
    "GET": "view",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}

RBAC_CACHE_TIMEOUT = 300


def normalize_permission_key(permission_key):
    if not permission_key:
        return None

    key = str(permission_key).strip()
    if "." not in key:
        return key.lower()

    module, action = key.split(".", 1)
    normalized_action = LEGACY_ACTION_MAP.get(action.upper(), action).lower()
    return f"{module.lower()}.{normalized_action}"


def permission_key_for_request(request, view):
    permission_required = getattr(view, "permission_required", None)

    if isinstance(permission_required, dict):
        permission_key = permission_required.get(request.method)
        if permission_key:
            return normalize_permission_key(permission_key)

    if isinstance(permission_required, (list, tuple, set)):
        return [normalize_permission_key(key) for key in permission_required]

    if isinstance(permission_required, str):
        return normalize_permission_key(permission_required)

    module = getattr(view, "permission_module", None) or getattr(view, "module", None)
    action = (
        getattr(view, "permission_action", None)
        or getattr(view, "action", None)
        or HTTP_ACTION_MAP.get(request.method)
    )

    if not module or not action:
        return None

    return normalize_permission_key(f"{module}.{action}")


def is_superadmin(user):
    if not user or not getattr(user, "is_authenticated", False):
        return False

    cache_key = f"rbac:superadmin:{user.pk}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    from access_control.models import UserRole

    result = UserRole.objects.filter(
        user=user,
        is_superadmin=True,
        role__is_active=True,
    ).exists()
    cache.set(cache_key, result, RBAC_CACHE_TIMEOUT)
    return result


def _enabled_permissions(permission_payload):
    permissions = set()
    disabled = set()

    for key, enabled in (permission_payload or {}).items():
        normalized_key = normalize_permission_key(key)
        if not normalized_key:
            continue

        if enabled:
            permissions.add(normalized_key)
        else:
            disabled.add(normalized_key)

    return permissions, disabled


def get_user_permission_keys(user):
    if not user or not getattr(user, "is_authenticated", False):
        return set()

    cache_key = f"rbac:permissions:{user.pk}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    from access_control.models import RolePermission, UserPermission

    permission_keys = set()

    role_permissions = RolePermission.objects.filter(
        role__userrole__user=user,
        role__is_active=True,
    )
    for role_permission in role_permissions:
        enabled, _ = _enabled_permissions(role_permission.permissions)
        permission_keys.update(enabled)

    user_permission = UserPermission.objects.filter(user=user).first()
    if user_permission:
        enabled, disabled = _enabled_permissions(user_permission.permissions)
        permission_keys.difference_update(disabled)
        permission_keys.update(enabled)

    cache.set(cache_key, permission_keys, RBAC_CACHE_TIMEOUT)
    return permission_keys


def clear_user_rbac_cache(user_id):
    cache.delete_many([
        f"rbac:superadmin:{user_id}",
        f"rbac:permissions:{user_id}",
    ])


def user_has_permission(user, permission_key):
    if is_superadmin(user):
        return True

    if isinstance(permission_key, (list, tuple, set)):
        return all(user_has_permission(user, key) for key in permission_key)

    normalized_key = normalize_permission_key(permission_key)
    if not normalized_key:
        return False

    return normalized_key in get_user_permission_keys(user)


def log_permission_denied(request, permission_key):
    user = getattr(request, "user", None)
    logger.warning(
        "RBAC denied user_id=%s path=%s method=%s permission=%s",
        getattr(user, "pk", None),
        getattr(request, "path", None),
        getattr(request, "method", None),
        permission_key,
    )


def _accessible_department_ids(user):
    from access_control.models import DepartmentAccess
    from departments.models import Division

    ids = set(
        DepartmentAccess.objects.filter(user=user).values_list("department_id", flat=True)
    )
    if getattr(user, "department_id", None):
        ids.add(user.department_id)
    division_ids = _accessible_division_ids(user)
    if division_ids:
        ids.update(
            Division.objects.filter(id__in=division_ids).values_list("department_id", flat=True)
        )
    return ids


def _accessible_division_ids(user):
    from access_control.models import DivisionAccess

    ids = set(DivisionAccess.objects.filter(user=user).values_list("division_id", flat=True))
    if getattr(user, "division_id", None):
        ids.add(user.division_id)
    return ids


def _accessible_client_ids(user):
    from access_control.models import ClientAccess

    return set(ClientAccess.objects.filter(user=user).values_list("client_id", flat=True))


def filter_queryset_for_user(user, queryset, resource):
    if is_superadmin(user):
        return queryset

    if resource == "department":
        department_ids = _accessible_department_ids(user)
        query = Q(created_by=user)
        if department_ids:
            query |= Q(id__in=department_ids)
        return queryset.filter(query) if query.children else queryset.none()

    if resource == "division":
        from access_control.models import DepartmentAccess

        division_ids = _accessible_division_ids(user)
        department_ids = set(
            DepartmentAccess.objects.filter(user=user).values_list("department_id", flat=True)
        )
        query = Q(created_by=user)
        if division_ids:
            query |= Q(id__in=division_ids)
        if department_ids:
            query |= Q(department_id__in=department_ids)
        return queryset.filter(query) if query.children else queryset.none()

    if resource == "client":
        client_ids = _accessible_client_ids(user)
        query = Q(created_by=user)
        if client_ids:
            query |= Q(id__in=client_ids)
        return queryset.filter(query) if query.children else queryset.none()

    if resource == "project":
        from teams.models import ProjectTeamMember

        department_ids = _accessible_department_ids(user)
        division_ids = _accessible_division_ids(user)
        client_ids = _accessible_client_ids(user)
        team_project_ids = set(
            ProjectTeamMember.objects.filter(user=user).values_list("project_id", flat=True)
        )

        query = Q()
        if department_ids:
            query |= Q(department_id__in=department_ids)
        if division_ids:
            query |= Q(division_id__in=division_ids)
        if client_ids:
            query |= Q(client_id__in=client_ids)
        if team_project_ids:
            query |= Q(id__in=team_project_ids)
        query |= Q(created_by=user)

        return queryset.filter(query) if query.children else queryset.none()

    if resource == "team":
        from projects.models import Project

        project_ids = filter_queryset_for_user(
            user,
            Project.objects.all(),
            "project",
        ).values_list("id", flat=True)
        return queryset.filter(project_id__in=project_ids)

    if resource == "user":
        department_ids = _accessible_department_ids(user)
        division_ids = _accessible_division_ids(user)
        query = Q(id=user.id)
        if division_ids:
            query |= Q(division_id__in=division_ids)
        if department_ids:
            query |= Q(department_id__in=department_ids)
        return queryset.filter(query)

    if resource == "audit":
        return queryset.filter(user=user)

    return queryset
