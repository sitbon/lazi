from django.conf import settings
from django.urls import include, path
from django.contrib import admin


urlpatterns = [
    path("", admin.site.urls),
    # path("admin/", include(wagtailadmin_urls)),
    # path("documents/", include(wagtaildocs_urls)),
    # path("search/", search_views.search, name="search"),
    # path("sitemap.xml", sitemap),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
