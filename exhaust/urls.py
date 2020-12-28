from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from markdownx.views import MarkdownifyView

from exhaust.posts.sitemaps import POSTS_SITE_MAPS

urlpatterns = [
    path('', include('exhaust.posts.urls', namespace='posts')),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('admin/', admin.site.urls),
    path('markdownx/markdownify/', MarkdownifyView.as_view(), name='markdownx_markdownify'),
    path('sitemap.xml', sitemap, {'sitemaps': POSTS_SITE_MAPS}, name='django.contrib.sitemaps.views.sitemap'),
] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
)

if settings.DEBUG:
    # Error page styling tests.
    urlpatterns += [
        path('404/', TemplateView.as_view(template_name='404.html')),
        path('500/', TemplateView.as_view(template_name='500.html')),
    ]
