from unittest.mock import MagicMock

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from exhaust.common.templatetags.markdown import markdown
from exhaust.common.templatetags.pagination import pagination_url
from exhaust.common.templatetags.rss import path_to_url, rss_post_body
from exhaust.posts.models import Post


class TagsTestCase(TestCase):
    def test_pagination_url(self):
        class FakeResolverMatch:
            # For some reason MagicMock won't work for this. I don't know why.
            def __init__(self):
                self.namespace = 'posts'
                self.url_name = 'post_list'
                self.args = []
                self.kwargs = {}

        context = {
            'request': MagicMock(
                # resolver_match=FakeResolverMatch(),
                resolver_match=FakeResolverMatch()
            )
        }

        # page=1 should not pass the 'page' argument.
        self.assertEqual(pagination_url(context, 1), '/')
        # but page=ANYTHINGELSE should
        self.assertEqual(pagination_url(context, 2), '/page/2/')

    def test_markdown(self):
        # More tests are in test case for MarkdownRenderer and markdown_to_html.
        # Just make sure this is not totally broken and rely on those tests
        # (and those in CommonMark) to ensure it's doing what it should.
        text = '\n'.join([
            'Testing',
            '', '',
            '123',
        ])
        self.assertEqual(markdown(text).strip(), '<p>Testing</p>\n<p>123</p>')

    @override_settings(DEBUG=False, SITE_DOMAIN='example.com')
    def test_rss_html(self):
        # Ensure that all tags are being converted for use in RSS
        # appropriately.
        post = Post.objects.create(
            title='Hello',
            text='\n'.join([
                '<img src="/some-image/">',
                '<picture>',
                ' <source src="/another-image/">',
                '</picture>',
                '<a href="/boat/">boat</a>',
                '<div class="image__padder"></div>',
                '<div class="image" style="max-width: 100px"></div>'
            ]),
            author=get_user_model().objects.create(username='lewis', password='lewis')
        )
        soup = BeautifulSoup(rss_post_body(post), 'html.parser')
        self.assertEqual(soup.find('img')['src'], 'https://example.com/some-image/')
        self.assertEqual(soup.find('a')['href'], 'https://example.com/boat/')
        self.assertEqual(soup.find('picture').find('source')['src'], 'https://example.com/another-image/')
        self.assertIs(soup.find('div', attrs={'class': 'image__padder'}), None)
        self.assertEqual(soup.find('div', attrs={'class': 'image'})['style'], '')

    def test_path_to_url(self):
        self.assertEqual(path_to_url('https://www.example.com'), 'https://www.example.com')
        self.assertEqual(path_to_url('http://www.example.com'), 'http://www.example.com')

        with override_settings(DEBUG=True):
            self.assertEqual(path_to_url('/boat/'), 'http://localhost:8000/boat/')

        with override_settings(DEBUG=False, SITE_DOMAIN='example.com'):
            self.assertEqual(path_to_url('/boat/'), 'https://example.com/boat/')
