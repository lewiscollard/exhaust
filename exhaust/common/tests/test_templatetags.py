from unittest.mock import MagicMock

from django.http import QueryDict
from django.test import TestCase

from exhaust.common.templatetags.markdown import markdown
from exhaust.common.templatetags.pagination import pagination_url


class TagsTestCase(TestCase):
    def test_pagination_url(self):
        def generate_context(get_params=None):
            get = QueryDict('', mutable=True)
            get.update(get_params or {})
            return {
                'request': MagicMock(
                    path='/test/',
                    GET=get,
                )
            }

        # page=1 should not append a GET parameter.
        self.assertEqual(pagination_url(generate_context(), 1), '/test/')
        # but page=ANYTHINGELSE should
        self.assertEqual(pagination_url(generate_context(), 2), '/test/?page=2')

        # Ensure that query strings are being reconstructed appropriately in
        # both cases.
        self.assertEqual(pagination_url(generate_context({'test': 'wat'}), 1), '/test/?test=wat')
        self.assertEqual(pagination_url(generate_context({'test': 'wat'}), 2), '/test/?test=wat&page=2')

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
