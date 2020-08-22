from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from exhaust.posts.sitemaps import POSTS_SITE_MAPS

urlpatterns = [
    path('', include('exhaust.posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': POSTS_SITE_MAPS}, name='django.contrib.sitemaps.views.sitemap'),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)
