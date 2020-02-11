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
    urlpatterns += static(
        prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )


# Reference:
#   https://github.com/bernardopires/django-tenant-schemas/issues/222
# Explanation:
#   Well, normally this should be placed inside the `if settings.DEBUG`, but it
#   seems like the position of this AFFECT one of my test (test_admin.py), it
#   indeed would pass after I modified the URL patterns like this right now :P
import debug_toolbar  # noqa

urlpatterns += [
    path("__debug__/", include(debug_toolbar.urls)),
]
