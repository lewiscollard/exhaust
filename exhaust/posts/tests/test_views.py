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
            date=now(),
        )

        post_without_slug = Post.objects.create(
            author=self.author,
            date=now(),
            text='bargle',
        )

        possibles = [
            # Post with slug called with PK argument only should redirect.
            reverse('posts:post_detail', kwargs={'pk': post_with_slug.pk}),
            # Rewrite garbage in the slug.
            reverse('posts:post_detail', kwargs={'pk': post_with_slug.pk, 'slug': 'some-garbage-value'})
        ]
        for path in possibles:
            response = self.client.get(path)
            self.assertRedirects(response, post_with_slug.get_absolute_url(), status_code=301, target_status_code=200)

        # Test that putting a slug after the pk argument on a post without a
        # slug redirects.
        response = self.client.get(reverse('posts:post_detail', kwargs={'pk': post_without_slug.pk, 'slug': 'anything-at-all'}))
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
