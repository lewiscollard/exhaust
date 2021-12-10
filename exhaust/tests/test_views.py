from urllib.parse import urlparse

from django.test import TestCase
from django.urls import reverse


class RobotsTestCase(TestCase):
    def test_robots_works(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)

        sitemap_line = next(
            line for line in response.content.decode('utf8').split('\n')
            if line.startswith('Sitemap: ')
        )
        parsed = urlparse(sitemap_line.split(' ')[1])
        self.assertEqual(parsed.path, reverse('django.contrib.sitemaps.views.sitemap'))
