from datetime import timedelta
from xml.etree import ElementTree

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import now

from exhaust.posts.models import Post, PostImage
from exhaust.posts.urls import urlpatterns as post_urlpatterns
from exhaust.posts.views import PostViewMixin
from exhaust.tests.factories import (CategoryFactory, PostFactory,
                                     PostImageFactory, UserFactory)
from exhaust.tests.helpers import get_test_file_path


class PostViewsTestCase(TestCase):
    def test_detail_doesnt_raise_exception(self):
        # Ensure that accessing a post that does not exist does a 404, rather
        # than raising an exception.
        response = self.client.get(reverse('posts:post_detail', kwargs={'identifier': 999, 'slug': 'please-dont-raise-exception'}))
        self.assertEqual(response.status_code, 404)

    def test_detail_redirects(self):
        post_with_slug = PostFactory.create(slug='slug', online=True)

        post_without_slug = PostFactory.create(slug='', online=True)

        possibles = [
            # Post with slug called with identifier argument only should redirect.
            reverse('posts:post_detail', kwargs={'identifier': post_with_slug.identifier}),
            # Rewrite garbage in the slug.
            reverse('posts:post_detail', kwargs={'identifier': post_with_slug.identifier, 'slug': 'some-garbage-value'})
        ]
        for path in possibles:
            response = self.client.get(path)
            self.assertRedirects(response, post_with_slug.get_absolute_url(), status_code=301, target_status_code=200)

        # Test that putting a slug after the identifier argument on a post without a
        # slug redirects.
        response = self.client.get(reverse('posts:post_detail', kwargs={'identifier': post_without_slug.identifier, 'slug': 'anything-at-all'}))
        self.assertRedirects(response, post_without_slug.get_absolute_url(), status_code=301, target_status_code=200)

    def test_category_view(self):
        category = CategoryFactory.create(meta_description='Test!', description='Test')
        post = PostFactory.create(online=True)
        post.categories.add(category)

        # create another uncategorised post
        other_post = PostFactory.create(online=True)

        response = self.client.get(reverse('posts:post_category_list', kwargs={'category': category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object'], category)
        self.assertNotIn(other_post, response.context_data['object_list'])

        # Ensure that the "has SEO title" branch is checked in the template.
        category.seo_title = 'Search engine optimised!'
        category.save()
        response = self.client.get(reverse('posts:post_category_list', kwargs={'category': category.slug}))
        self.assertEqual(response.status_code, 200)

    def test_queryset_excludes_when_appropriate(self):
        # Add a draft post...
        draft_post = PostFactory.create(online=False, date=now() + timedelta(days=2))

        # ...and a future one...
        future_post = PostFactory.create(online=True, date=now() + timedelta(days=2))

        # ...and one that is live now.
        published_post = PostFactory.create(online=True)

        # We're not logged in, so we should only see the live post.
        response = self.client.get(reverse('posts:post_list'))
        self.assertEqual(len(response.context_data['object_list']), 1)

        # Check the detail views as well. Published ones should work:
        response = self.client.get(reverse('posts:post_detail', kwargs={'slug': published_post.slug, 'identifier': published_post.identifier}))
        self.assertEqual(response.status_code, 200)
        # But unpublished ones should not.
        for post in [draft_post, future_post]:
            response = self.client.get(reverse('posts:post_detail', kwargs={'slug': post.slug, 'identifier': post.identifier}))
            self.assertEqual(response.status_code, 404)

        # Now create a staff user and log in to it.
        get_user_model().objects.create_superuser(username='lewis', email='lewis@lewiscollard.com', password='lewis')
        self.client.login(username='lewis', password='lewis')
        # When we're logged in we should see all of the draft posts.
        response = self.client.get(reverse('posts:post_list'))
        self.assertEqual(len(response.context_data['object_list']), 3)

        # And so should their detail views.
        for post in [draft_post, future_post, published_post]:
            response = self.client.get(reverse('posts:post_detail', kwargs={'slug': post.slug, 'identifier': post.identifier}))
            self.assertEqual(response.status_code, 200)

    def test_list_redirects_page_querystring(self):
        response = self.client.get(f'{reverse("posts:post_list")}?page=2')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/page/2/')

    def test_all_views_inherit_from_postmixin(self):
        # Sanity check to ensure that all Post-wrangling views inherit from
        # PostMixin, so that it cannot accidentally bypass the above code.
        for pattern in post_urlpatterns:
            view_class = pattern.callback.view_class
            if not hasattr(view_class, 'model'):
                continue

            if view_class.model == Post:
                self.assertTrue(issubclass(pattern.callback.view_class, PostViewMixin))

    def _rss_response_is_sane(self, response, *, expected_item_count):
        # In lieu of a full validator, let's just make sure it looks
        # something like XML (in which case etree will fail to read it) and
        # looks vaguely like a feed, and has the expected number of items.
        tree = ElementTree.fromstring(response.content.decode('utf-8'))
        channel = tree.find('channel')
        self.assertEqual(len(channel.findall('item')), expected_item_count)

    def test_rss_feed(self):
        PostFactory.create_batch(5, online=True)

        posts_url = reverse('posts:post_feed')

        # Check the "secret" debug branch
        with override_settings(DEBUG=True):
            response = self.client.get(posts_url, {'debug': 'yep'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        response = self.client.get(posts_url)
        self.assertEqual(response.status_code, 200)
        self._rss_response_is_sane(response, expected_item_count=5)

    def test_category_feed_view(self):
        category = CategoryFactory.create()
        post = PostFactory.create(online=True)
        post.categories.add(category)

        # Check queryset exclusion for other categories...
        PostFactory.create_batch(2, online=True)
        # ...and ensure that offline posts are being excluded.
        offline_post = PostFactory.create(online=False)
        offline_post.categories.add(category.pk)

        response = self.client.get(reverse('posts:post_category_feed', kwargs={'category': category.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context_data['object_list']), [post])
        self._rss_response_is_sane(response, expected_item_count=1)

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        THUMBNAIL_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/',
    )
    def test_imageredirectview(self):
        image = PostImageFactory(image='large-image.jpg')
        # ensure it doesn't work for unauthenticated users
        response = self.client.get(reverse('posts:image_redirect', args=[image.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(reverse(settings.LOGIN_URL)))

        user = UserFactory(is_staff=True)
        self.client.force_login(user)

        response = self.client.get(reverse('posts:image_redirect', args=[image.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], image.image.url)

    def test_imageuploadview_unauthed(self):
        with open(get_test_file_path('small-image.jpg'), 'rb') as fd:
            response = self.client.post(reverse('posts:image_upload'), data={'image': fd})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(reverse(settings.LOGIN_URL)))

    def test_imageuploadview_with_junk(self):
        self.client.force_login(UserFactory.create(is_staff=True))

        with open(get_test_file_path('text-file.md'), 'rb') as fd:
            response = self.client.post(reverse('posts:image_upload'), data={'image': fd})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['image'], 'Image missing or broken.')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        THUMBNAIL_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_imageuploadview_happy_path(self):
        # pollution canary
        self.assertEqual(PostImage.objects.count(), 0)
        self.client.force_login(UserFactory.create(is_staff=True))

        with open(get_test_file_path('large-image.jpg'), 'rb') as fd:
            response = self.client.post(reverse('posts:image_upload'), data={'image': fd})
        self.assertEqual(response.status_code, 200)
        image = PostImage.objects.first()
        self.assertEqual(response.json()['image_code'], f'![]({image.get_absolute_url()})')
