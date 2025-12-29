from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    # APIs
    path("api/", include("accounts.urls")),
    path("api/access-control/", include("access_control.urls")),
    path("api/departments/", include("departments.urls")),
    path("api/designations/", include("designations.urls")),
    path("api/clients/", include("clients.urls")),
    path("api/projects/", include("projects.urls")),
    path("api/projects/", include("teams.urls")),
    path("api/audit/", include("audit.urls")),
]
