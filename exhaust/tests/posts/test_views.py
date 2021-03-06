from datetime import timedelta
from xml.etree import ElementTree

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import now

from exhaust.posts.models import Category, Post
from exhaust.posts.urls import urlpatterns as post_urlpatterns
from exhaust.posts.views import PostViewMixin


class PostViewsTestCase(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create(username='admin')

    def test_detail_doesnt_raise_exception(self):
        # Ensure that accessing a post that does not exist does a 404, rather
        # than raising an exception.
        response = self.client.get(reverse('posts:post_detail', kwargs={'identifier': 999, 'slug': 'please-dont-raise-exception'}))
        self.assertEqual(response.status_code, 404)

    def test_detail_redirects(self):
        post_with_slug = Post.objects.create(
            title='bargle',
            slug='slug',
            author=self.author,
            # the manager replaces seconds & microseconds with 0
            date=now() - timedelta(minutes=1),
            online=True,
        )

        post_without_slug = Post.objects.create(
            author=self.author,
            date=now() - timedelta(minutes=1),
            text='bargle',
            online=True,
        )

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
        category = Category.objects.create(title='Test category', slug='test-category', description='Testing!', meta_description='Test!')
        post = Post.objects.create(title='Test post', author=self.author, slug='test-post', online=True)
        post.categories.add(category)

        # create another uncategorised post
        other_post = Post.objects.create(title='Test post', author=self.author, slug='test-post', online=True)

        response = self.client.get(reverse('posts:post_category_list', kwargs={'slug': category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object'], category)
        self.assertNotIn(other_post, response.context_data['object_list'])

        # Ensure that the "has SEO title" branch is checked in the template.
        category.seo_title = 'Search engine optimised!'
        category.save()
        response = self.client.get(reverse('posts:post_category_list', kwargs={'slug': category.slug}))
        self.assertEqual(response.status_code, 200)

    def test_queryset_excludes_when_appropriate(self):
        # Add a draft post...
        draft_post = Post.objects.create(
            title='Draft',
            slug='draft',
            online=False,
            date=now() + timedelta(days=2),
            author=self.author,
        )

        # ...and a future one...
        future_post = Post.objects.create(
            title='Future',
            slug='flying-cars',
            online=True,
            date=now() + timedelta(days=2),
            author=self.author,
        )

        # ...and one that is live now.
        published_post = Post.objects.create(
            title='Published',
            slug='published',
            online=True,
            date=now() - timedelta(minutes=2),
            author=self.author,
        )

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

    def test_rss_feed(self):
        for i in range(1, 6):
            Post.objects.create(
                title=f'Test post {i}',
                slug=f'test-post-{i}',
                text='unimportant',
                author=self.author,
                online=True,
                date=now() - timedelta(minutes=1)
            )

        posts_url = reverse('posts:post_feed')

        # Check the "secret" debug branch
        with override_settings(DEBUG=True):
            response = self.client.get(posts_url, {'debug': 'yep'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')

        # In lieu of a full validator, let's just make sure it looks
        # something like XML (in which case etree will fail to read it) and
        # looks vaguely like a feed.
        response = self.client.get(posts_url)
        self.assertEqual(response.status_code, 200)

        tree = ElementTree.fromstring(response.content.decode('utf-8'))
        channel = tree.find('channel')
        self.assertEqual(len(channel.findall('item')), 5)
