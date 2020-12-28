from datetime import timedelta
from xml.etree import ElementTree  # nosec

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from exhaust.posts.models import Category, Post


class SitemapsTestCase(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create(username='admin')

    def test_posts_sitemap(self):
        for i in range(1, 6):
            Post.objects.create(
                title=f'Test post {i}',
                slug=f'test-post-{i}',
                text='unimportant',
                author=self.author,
                online=True,
                date=now() - timedelta(minutes=1)
            )

        # Check that offline ones aren't being shown.
        Post.objects.create(
            title=f'Test post {i}',
            slug=f'test-post-{i}',
            text='unimportant',
            author=self.author,
            online=False,
            date=now() - timedelta(minutes=1)
        )

        # ...and ones with a future publication date.
        Post.objects.create(
            title=f'Test post {i}',
            slug=f'test-post-{i}',
            text='unimportant',
            author=self.author,
            online=True,
            date=now() + timedelta(days=1)
        )

        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap'))
        self.assertEqual(response.status_code, 200)

        tree = ElementTree.fromstring(response.content.decode('utf-8'))  # nosec
        self.assertEqual(len(list(tree)), 5)

    def test_categories_sitemap(self):
        # Ensure unused categories are not shown in the sitemap, which
        # includes those that are only assigned to a post that is offline.
        used_category = Category.objects.create(title='In use', slug='in-use')
        unused_category = Category.objects.create(title='Unused', slug='unused')
        unused_category_2 = Category.objects.create(title='Unused', slug='unused')

        post = Post.objects.create(
            title='Test post',
            slug='test-post',
            text='unimportant',
            author=self.author,
            online=True,
            date=now() - timedelta(minutes=2)
        )
        post.categories.set([used_category])

        offline_post = Post.objects.create(
            title='Offline post',
            slug='offline-post',
            text='unimportant',
            author=self.author,
            online=False,
            date=now() - timedelta(minutes=1),
        )
        offline_post.categories.set([unused_category_2])

        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap'))
        self.assertEqual(response.status_code, 200)

        tree = ElementTree.fromstring(response.content.decode('utf-8'))  # nosec
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
