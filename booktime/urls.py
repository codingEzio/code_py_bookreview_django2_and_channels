from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from main import admin


urlpatterns = [
    path(route="admin/", view=admin.main_admin.urls, name="admin"),
    path(
        route="office-admin/",
        view=admin.central_office_admin.urls,
        name="office-admin",
    ),
    path(
        route="dispatch-admin/",
        view=admin.dispatchers_admin.urls,
        name="dispatch-admin",
    ),
    path(route="api-auth/", view=include(arg="rest_framework.urls")),
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
