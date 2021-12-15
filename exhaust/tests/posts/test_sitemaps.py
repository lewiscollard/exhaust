from datetime import timedelta
from xml.etree import ElementTree

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from exhaust.tests.factories import CategoryFactory, PostFactory


class SitemapsTestCase(TestCase):
    def test_posts_sitemap(self):
        PostFactory.create_batch(5, online=True)

        # Check that offline ones aren't being shown.
        PostFactory.create(online=False, date=now() - timedelta(minutes=1))

        # ...and ones with a future publication date.
        PostFactory.create(online=True, date=now() + timedelta(days=1))

        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap'))
        self.assertEqual(response.status_code, 200)

        tree = ElementTree.fromstring(response.content.decode('utf-8'))
        self.assertEqual(len(list(tree)), 5)

    def test_categories_sitemap(self):
        # Ensure unused categories are not shown in the sitemap, which
        # includes those that are only assigned to a post that is offline.
        used_category, unused_category, unused_category_2 = CategoryFactory.create_batch(3)

        post = PostFactory.create(online=True)
        post.categories.set([used_category])

        offline_post = PostFactory.create(online=False)
        offline_post.categories.set([unused_category_2])

        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap'))
        self.assertEqual(response.status_code, 200)

        tree = ElementTree.fromstring(response.content.decode('utf-8'))
        child_items = list(tree)
        self.assertEqual(len(child_items), 2)
        nsinfo = {'sitemaps': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        for obj in [post, used_category]:
            self.assertEqual(len([
                True for child in child_items
                if child.find('sitemaps:loc', nsinfo).text == f'http://testserver{obj.get_absolute_url()}'
            ]), 1)

        for obj in [unused_category, unused_category_2]:
            self.assertEqual(len([
                True for child in child_items
                if child.find('sitemaps:loc', nsinfo).text == f'http://testserver{obj.get_absolute_url()}'
            ]), 0)
