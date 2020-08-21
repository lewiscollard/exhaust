from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from ..models import Category, Post


class PostViewsTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create(username='admin')

    def test_detail_redirects(self):
        post_with_slug = Post.objects.create(
            title='bargle',
            slug='slug',
            author=self.author,
            # the manager replaces seconds & microseconds with 0
            date=now() - timedelta(minutes=1),
        )

        post_without_slug = Post.objects.create(
            author=self.author,
            date=now()  - timedelta(minutes=1),
            text='bargle',
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
        category = Category.objects.create(title='Test category', slug='test-category')
        post = Post.objects.create(title='Test post', author=self.author, slug='test-post')
        post.categories.add(category)

        # create another uncategorised post
        other_post = Post.objects.create(title='Test post', author=self.author, slug='test-post')

        response = self.client.get(reverse('posts:post_category_list', kwargs={'slug': category.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object'], category)
        self.assertNotIn(other_post, response.context_data['object_list'])
