from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(route="api-auth/", view=include(arg="rest_framework.urls")),
    path(route="admin/", view=admin.site.urls),
    path(route="", view=include("main.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(
        prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
