import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import File
from django.test import TestCase, override_settings
from django.utils.timezone import now

from exhaust.posts.models import Attachment, Post, PostImage


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

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_post_str(self):
        post = Post.objects.create(title='Testing!', author=self.author)
        self.assertEqual(str(post), 'Testing!')

        post = Post.objects.create(title='', text='Body', author=self.author)
        self.assertEqual(str(post), 'Body')

        post = Post.objects.create(title='', text='a' * 41, author=self.author)
        self.assertEqual(str(post), ('a' * 38) + '...')

        post = Post.objects.create(title='', text='', author=self.author)
        self.assertEqual(str(post), '(Broken post)')

        # Check with a "real" image. The real tests are already done for
        # render_multiformat_image. We'll only make sure it looks something
        # like what we expect.
        post = Post.objects.create(title='', text='', author=self.author)
        image = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'small-image.jpg'))
        with open(image, mode='rb') as fd:
            post.image.save('small-image.jpg', File(fd, name='test-image.jpg'))

        self.assertEqual(str(post), 'Image post: small-image.jpg')

    def test_post_get_title_link_url(self):
        post = Post.objects.create(title='Test', text='Something', author=self.author)
        self.assertEqual(post.get_title_link_url(), post.get_absolute_url())

        post = Post.objects.create(title='Test', text='Something', link='https://example.invalid', author=self.author)
        self.assertEqual(post.get_title_link_url(), 'https://example.invalid')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_post_image_str(self):
        image = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'small-image.jpg'))
        post_image = PostImage()
        with open(image, 'rb') as fd:
            post_image.image.save('small-image.jpg', File(fd))
        post_image.save()
        self.assertIs(str(post_image).startswith('small-image'), True)
        self.assertIs(str(post_image).endswith('.jpg'), True)

        post_image.title = 'Test'
        self.assertEqual(str(post_image), 'Test')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_post_image_get_absolute_url(self):
        image = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'small-image.jpg'))
        post_image = PostImage()
        with open(image, 'rb') as fd:
            post_image.image.save('small-image.jpg', File(fd))
        post_image.save()
        self.assertEqual(post_image.get_absolute_url(), f'/image-redirect/{post_image.pk}/')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_attachment_str(self):
        image = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'small-image.jpg'))
        attachment = Attachment()
        with open(image, 'rb') as fd:
            attachment.file.save('small-image.jpg', File(fd))
        attachment.save()
        self.assertEqual(str(attachment), 'small-image.jpg')
