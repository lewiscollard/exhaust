from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import now

from ..models import Post


class PostModelTestCase(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create(username='admin')

    def test_post_status_text(self):
        # If is_online is false, it should always show as "Draft"
        post = Post.objects.create(
            title='Draft',
            slug='draft',
            online=False,
            date=now() - timedelta(minutes=2),
            author=self.author,
        )
        self.assertEqual(post.status_text, 'Draft')

        # ...even if the publication date is a future date (when online=True
        # it'll be "Scheduled").
        post = Post.objects.create(
            title='Draft 2',
            slug='draft-2',
            online=False,
            date=now() + timedelta(days=2),
            author=self.author,
        )
        self.assertEqual(post.status_text, 'Draft')

        # Check future-scheduled posts.
        post = Post.objects.create(
            title='Draft 2',
            slug='draft-2',
            online=True,
            date=now() + timedelta(days=2),
            author=self.author,
        )
        self.assertEqual(post.status_text, 'Scheduled')

        # And one that is live now.
        post = Post.objects.create(
            title='Draft 2',
            slug='draft-2',
            online=True,
            date=now() - timedelta(minutes=2),
            author=self.author,
        )
        self.assertEqual(post.status_text, 'Published')
