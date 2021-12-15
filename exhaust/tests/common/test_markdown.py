from bs4 import BeautifulSoup
from django.test import TestCase, override_settings
from django.urls import reverse

from exhaust.common.markdown import markdown_to_html
from exhaust.tests.factories import PostImageFactory


class MarkdownTestCase(TestCase):
    def test_youtube_video_renders(self):
        video_id = '4bQ6h0DPuHQ'
        rendered = markdown_to_html(f'<youtube id="{video_id}" />')
        soup = BeautifulSoup(rendered, features='html.parser')
        wrapper = soup.find(attrs={'class': 'vue-youtube-mount'})
        self.assertEqual(len(wrapper.find_all('youtube-video')), 1)
        self.assertEqual(wrapper.find('youtube-video')['id'], video_id)

        # this is stupid but should not throw an exception
        markdown_to_html('<youtube />')

    def test_malicious_things(self):
        # We're not going to test every possible malicious thing - if that is
        # the case, Bleach is not working and we are going to have a bad time
        # (along with anyone else doing HTML sanitisation). Just be sure that
        # we've not inadvertently broken it.
        rendered = markdown_to_html('<script>alert(1)</script>')
        self.assertEqual(rendered.strip(), '&lt;script&gt;alert(1)&lt;/script&gt;')
        soup = BeautifulSoup(rendered, features='html.parser')
        self.assertEqual(soup.find('script'), None)

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
    def test_markdown_images(self):
        # Test multiformat renderer does not attempt to handle off-site images.
        rendered = markdown_to_html('![](https://www.example.com/off-site-image/)')
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertEqual(soup.find('img')['src'], 'https://www.example.com/off-site-image/')

        # Check the branch that tests non-existent post images.
        url = reverse('posts:image_redirect', kwargs={'pk': '999999999999'})
        rendered = markdown_to_html(f'![]({url})')
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertIs(soup.find('img'), None)

        # Check the branch that looks for garbage (bad URL reversing)
        url = '/image-redirect/*****/'
        rendered = markdown_to_html(f'![]({url})')
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertIs(soup.find('img'), None)

        # Check with a "real" image. The real tests are already done for
        # render_multiformat_image. We'll only make sure it looks something
        # like what we expect.
        post_image = PostImageFactory(image='small-image.jpg')

        url = reverse('posts:image_redirect', kwargs={'pk': post_image.pk})
        rendered = markdown_to_html(f'![]({url})')
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertIsNot(soup.find('img'), None)
        self.assertIsNot(soup.find('picture'), None)

        # Be really sure we haven't done something to break alt text, because
        # we are a bit dependent on CommonMark's internals.
        rendered = markdown_to_html('![alt text](https://example.com/offsite-image.jpg)')
        soup = BeautifulSoup(rendered, 'html.parser')
        self.assertEqual(soup.find('img')['alt'], 'alt text')
