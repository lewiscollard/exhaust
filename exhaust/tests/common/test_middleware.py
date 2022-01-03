from test.support import EnvironmentVarGuard

from django.test import TestCase


class MiddlewareTestCase(TestCase):
    def test_csp_header_is_added(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Content-Security-Policy', response.headers)

    def test_csp_middleware_not_used_with_env_var_set(self):
        env = EnvironmentVarGuard()
        env.set('EXHAUST_DISABLE_CSP', '1')

        with env:
            response = self.client.get('/')
        self.assertNotIn('Content-Security-Policy', response.headers)
