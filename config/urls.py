from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Neobis-Threads-Team2-Back-end",
        default_version='v1',
        description="Neobis test REST API",
        # license=openapi.License(name="Apache License 2.0"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

swagger_info = schema_view.with_ui('swagger', cache_timeout=0)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('swagger/', swagger_info, name='swagger'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('accounts/', include('allauth.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),

    path('', include("users.urls")),
    path('', include("pages.urls")),
]
