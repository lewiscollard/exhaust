from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils.timezone import now

from exhaust.tests.factories import (AttachmentFactory, PostFactory,
                                     PostImageFactory)


class PostModelTestCase(TestCase):
    def test_post_status_text(self):
        # If `online` is false, it should always show as "Draft"
        post = PostFactory.create(online=False)
        self.assertEqual(post.status_text, 'Draft')

        # ...even if the publication date is a future date (when online=True
        # it'll be "Scheduled").
        post = PostFactory.create(online=False, date=now() + timedelta(days=2))
        self.assertEqual(post.status_text, 'Draft')

        # Check future-scheduled posts.
        post = PostFactory.create(online=True, date=now() + timedelta(days=2))
        self.assertEqual(post.status_text, 'Scheduled')

        # And one that is live now.
        post = PostFactory.create(online=True)
        self.assertEqual(post.status_text, 'Published')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_post_str(self):
        post = PostFactory.create(title='Testing!', online=True)
        self.assertEqual(str(post), 'Testing!')

        post = PostFactory.create(title='', text='Body', online=True)
        self.assertEqual(str(post), 'Body')

        # Test body truncation.
        post = PostFactory.create(title='', text='a' * 41, online=True)
        self.assertEqual(str(post), ('a' * 38) + '...')

        post = PostFactory.create(title='', text='', online=True)
        self.assertEqual(str(post), '(Broken post)')

        # Check with a "real" image. The real tests are already done for
        # render_multiformat_image. We'll only make sure it looks something
        # like what we expect.
        post = PostFactory.create(title='', text='', online=True, image='small-image.jpg')

        self.assertIs(str(post).startswith('Image post: small-image'), True)
        self.assertIs(str(post).endswith('.jpg'), True)

    def test_post_get_title_link_url(self):
        post = PostFactory.create(online=True)
        self.assertEqual(post.get_title_link_url(), post.get_absolute_url())

        post = PostFactory.create(link='https://example.invalid', online=True)
        self.assertEqual(post.get_title_link_url(), 'https://example.invalid')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_post_image_str(self):
        post_image = PostImageFactory.create(image='small-image.jpg')
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
        post_image = PostImageFactory.create(image='small-image.jpg')
        self.assertEqual(post_image.get_absolute_url(), f'/image-redirect/{post_image.pk}/')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        MEDIA_URL='/m/'
    )
    def test_attachment_str(self):
        attachment = AttachmentFactory(file='small-image.jpg')
        self.assertEqual(str(attachment), 'small-image.jpg')
