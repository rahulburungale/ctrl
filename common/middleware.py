from audit.services import log_action
from django.utils.deprecation import MiddlewareMixin

class AuditMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        try:
            if not hasattr(request, "user") or not request.user.is_authenticated:
                return response

            # Ignore non-business endpoints
            ignore_paths = [
                "/admin/",
                "/api/schema/",
                "/api/docs/",
                "/favicon.ico",
            ]

            if any(request.path.startswith(p) for p in ignore_paths):
                return response

            entity_id = None

            if hasattr(request, "resolver_match") and request.resolver_match:
                entity_id = request.resolver_match.kwargs.get("pk")

            if not entity_id and request.method in ["POST", "PUT", "PATCH"]:
                entity_id = request.data.get("id") or request.data.get("pk")

            action_map = {
                "GET": "VIEW",
                "POST": "CREATE",
                "PUT": "UPDATE",
                "PATCH": "UPDATE",
                "DELETE": "DELETE",
            }

            action = action_map.get(request.method, request.method)

            log_action(
                user=request.user,
                module=request.resolver_match.app_name or "SYSTEM",
                action=action,
                entity_id=entity_id,
                metadata={
                    "path": request.path,
                    "method": request.method,
                    "status": response.status_code,
                }
            )

        except Exception:
            pass

        return response
