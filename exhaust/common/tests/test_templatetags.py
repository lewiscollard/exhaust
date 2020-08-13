from unittest.mock import MagicMock

from django.http import QueryDict
from django.test import TestCase

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
