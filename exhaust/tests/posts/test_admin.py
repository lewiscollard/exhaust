from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from exhaust.posts.models import Post
from exhaust.tests.factories import (AttachmentFactory, CategoryFactory,
                                     PostFactory)


class PostAdminTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='admin',
            password='123',
            email='nobody@example.invalid',
        )
        self.client.force_login(self.user)

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=False,
        MEDIA_URL='/m/'
    )
    def test_quality_control_filter(self):
        # Ensure QualityControlListFilter works.
        cat = CategoryFactory.create()

        PostFactory.create(meta_description='test', online=True, categories=[cat])

        no_meta_post = PostFactory.create(online=True, categories=[cat])

        no_categories_post = PostFactory.create(meta_description='test', online=True)

        no_alt_text_post = PostFactory.create(
            title='No alt text',
            slug='no-alt-text',
            meta_description='Description',
            image='small-image.jpg',
            online=True,
        )
        no_alt_text_post.categories.set([cat])

        no_alt_text_in_body_post = PostFactory.create(
            meta_description='test',
            text='![](/some-image.jpg)',
            online=True,
        )
        no_alt_text_in_body_post.categories.set([cat])

        admin_url = reverse('admin:posts_post_changelist')
        response = self.client.get(admin_url)
        # sanity check
        self.assertEqual(len(response.context_data['cl'].result_list), 5)

        response = self.client.get(admin_url, {'quality_control': 'no_meta_description'})
        results = response.context_data['cl'].result_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], no_meta_post)

        response = self.client.get(admin_url, {'quality_control': 'no_categories'})
        results = response.context_data['cl'].result_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], no_categories_post)

        response = self.client.get(admin_url, {'quality_control': 'no_alt_text'})
        self.assertEqual(response.status_code, 200)
        results = response.context_data['cl'].result_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], no_alt_text_post)

        response = self.client.get(admin_url, {'quality_control': 'no_alt_text_body'})
        self.assertEqual(response.status_code, 200)
        results = response.context_data['cl'].result_list
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], no_alt_text_in_body_post)

        # Check the fall-through case, just to ensure full coverage.
        response = self.client.get(admin_url, {'quality_control': 'garbage'})
        self.assertEqual(len(response.context_data['cl'].result_list), 5)

    def test_prefetching_categories(self):
        cat = CategoryFactory.create()
        cat2 = CategoryFactory.create()

        PostFactory.create_batch(10, online=True, categories=[cat, cat2])

        # Baseload number of queries for loading the list, with no objects,
        # should be 5. That is getting the current session, getting the
        # current user, some savepoint thing (two queries, one for grab & one
        # for release), and getting the total count of posts. Our prefetching
        # should mean we only add 2 queries to this regardless of the number
        # of posts
        with self.assertNumQueries(7):
            response = self.client.get(reverse('admin:posts_post_changelist'))

        self.assertEqual(len(response.context_data['cl'].result_list), 10)

    def test_saving_post_sets_user(self):
        # Ensure saving the post sets the current user as the author.
        response = self.client.post(reverse('admin:posts_post_add'), {
            'title': 'author test',
            'text': 'author test!',
            'slug': 'author-test',
            'date_0': '2021-11-25',
            'date_1': '12:12:12',
        })
        self.assertEqual(response.status_code, 302)
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=False,
        MEDIA_URL='/m/'
    )
    def test_attachment_list_view(self):
        # Simple test of the list, sort-of tests the "link" thing in the
        # list_display, at least the "doesn't explode" part of it
        attachment = AttachmentFactory.create(file='small-image.jpg')

        response = self.client.get(reverse('admin:posts_attachment_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context_data['cl'].result_list), [attachment])
