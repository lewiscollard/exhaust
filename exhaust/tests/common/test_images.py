from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django.core.files.storage import default_storage
from django.test import TestCase, override_settings

from exhaust.common.images import render_multiformat_image
from exhaust.common.templatetags.assets import render_image
from exhaust.tests.factories import PostImageFactory


class ImagesTestCase(TestCase):
    def _check_rendered_image_html(self, html):
        # Tests that all the HTML from a rendered multiformat image is
        # sensible.
        soup = BeautifulSoup(html, 'html.parser')
        for picture_tag in soup.find_all('picture'):
            for source_tag in picture_tag.find_all('source'):
                url = source_tag['src']
                # are we deep enough in for loops yet?
                path = urlparse(url).path[3:]
                self.assertTrue(default_storage.exists(path))

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        THUMBNAIL_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        },
        # So we have a known fixed value, independent of whatever I decide to
        # use in prod some time.
        MEDIA_URL='/m/'
    )
    def test_render_multiformat_image(self):
        # Ensure that a large image renders reasonably.
        image = PostImageFactory(image='large-image.jpg')
        self._check_rendered_image_html(render_multiformat_image(image.image, width=720))
        # Make sure the template tag works as well.
        self._check_rendered_image_html(render_image(image.image, width=720))

        # Ensure the "never upscale" branch is visited.
        image = PostImageFactory(image='small-image.jpg')
        self._check_rendered_image_html(render_multiformat_image(image.image, width=720))

        # Check the "has a title" branch in the template.
        image = PostImageFactory(image='small-image.jpg')
        html = render_multiformat_image(image.image, width=720, title='Testing!')
        self._check_rendered_image_html(html)

        soup = BeautifulSoup(html, 'html.parser')
        self.assertEqual(len(soup.find_all('figure')), 1)
        self.assertEqual(len(soup.find_all('figcaption')), 1)
        self.assertEqual(soup.find('figcaption').text, 'Testing!')

    @override_settings(
        DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
        THUMBNAIL_STORAGE='inmemorystorage.InMemoryStorage',
        INMEMORYSTORAGE_PERSIST=True,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
        MEDIA_URL='/m/'
    )
    def test_render_multiformat_image_cache_branch(self):
        # Test that specifically ensures the "fetch cached version" branch is
        # checked, and that the cached version is exactly identical to
        # the uncached one
        image = PostImageFactory(image='large-image.jpg')
        rendered1 = render_multiformat_image(image.image, width=720)
        self._check_rendered_image_html(rendered1)

        rendered2 = render_multiformat_image(image.image, width=720)
        self.assertEqual(rendered1, rendered2)
