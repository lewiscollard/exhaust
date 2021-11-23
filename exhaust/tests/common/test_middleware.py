from django.test import TestCase


class MiddlewareTestCase(TestCase):
    def test_csp_header_is_added(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        assert 'Content-Security-Policy' in response.headers
