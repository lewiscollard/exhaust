from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from exhaust.posts.models import Category, Post


class PostAdminTestCase(TestCase):
    def setUp(self):
        # nosec
        self.user = get_user_model().objects.create_superuser(  # nosec
            username='admin',
            password='123',
            email='nobody@example.invalid',
        )
        self.client.login(username='admin', password='123')  # nosec

    def test_quality_control_filter(self):
        # Ensure QualityControlListFilter works.
        cat = Category.objects.create(title='Test cat', slug='test-cat')

        good_post = Post.objects.create(
            title='An optimised post',
            slug='good-post',
            author=self.user,
            meta_description='test',
        )
        good_post.categories.set([cat])

        no_meta_post = Post.objects.create(
            title='No meta description',
            slug='no-meta',
            author=self.user,
        )
        no_meta_post.categories.set([cat])

        no_categories_post = Post.objects.create(
            title='No categories',
            slug='no-categories',
            author=self.user,
            meta_description='test',
        )

        admin_url = reverse('admin:posts_post_changelist')
        response = self.client.get(admin_url)
        # sanity check
        self.assertEqual(len(response.context_data['cl'].result_list), 3)

        response = self.client.get(admin_url, {'quality_control': 'no_meta_description'})
        results = response.context_data['cl'].result_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], no_meta_post)

        response = self.client.get(admin_url, {'quality_control': 'no_categories'})
        results = response.context_data['cl'].result_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], no_categories_post)

        # Check the fall-through case, just to ensure full coverage.
        response = self.client.get(admin_url, {'quality_control': 'garbage'})
        self.assertEqual(len(response.context_data['cl'].result_list), 3)
