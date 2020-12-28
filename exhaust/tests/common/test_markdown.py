from bs4 import BeautifulSoup
from django.test import TestCase

from exhaust.common.markdown import markdown_to_html


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
