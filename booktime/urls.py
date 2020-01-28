from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path(route="admin/", view=admin.site.urls),
    path(route="", view=include("main.urls")),
]

if settings.DEBUG is True:
    urlpatterns += static(
        prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
