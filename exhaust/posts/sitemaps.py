from django.contrib.sitemaps import Sitemap

from .models import Category, Post


class PostSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.5

    def items(self):
        return Post.objects.select_published()

    def lastmod(self, obj):
        return obj.date


class CategorySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.1

    def items(self):
        # Only show categories that have a *published* article within them.
        return Category.objects.filter(
            post__id__in=Post.objects.select_published().values_list('id', flat=True)
        ).distinct()


POSTS_SITE_MAPS = {
    'posts': PostSitemap(),
    'categories': CategorySitemap(),
}
