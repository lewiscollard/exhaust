from bs4 import BeautifulSoup
from django.test import TestCase, override_settings
from django.urls import reverse

from exhaust.tests.factories import GramFactory, UserFactory


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
class AdminTestCase(TestCase):
    def setUp(self):
        self.client.force_login(UserFactory.create(is_staff=True, is_superuser=True))

    def test_admin_gram_list_image(self):
        GramFactory.create(image='small-image.jpg')
        response = self.client.get(reverse('admin:exogram_gram_changelist'))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features='html.parser')
        thumbnail = soup.select('table#result_list tbody tr th.field-get_thumbnail img')[0]
        self.assertIs(thumbnail['src'].startswith('/m/'), True)

    def test_admin_gram_list_commons_link(self):
        gram = GramFactory.create(image='small-image.jpg', commons_link='https://commons.wikimedia.org/xxx')
        response = self.client.get(reverse('admin:exogram_gram_changelist'))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features='html.parser')
        link = soup.select('table#result_list tbody tr td.field-get_commons_link a')[0]
        self.assertEqual(link['href'], gram.commons_link)
        gram.delete()

        GramFactory.create(image='small-image.jpg')
        response = self.client.get(reverse('admin:exogram_gram_changelist'))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features='html.parser')
        link_cell = soup.select('table#result_list tbody tr td.field-get_commons_link')[0]
        self.assertEqual(link_cell.text, '-')

    def test_admin_gram_get_form(self):
        # Ensure 'online' checkbox is checked by default.
        response = self.client.get(reverse('admin:exogram_gram_add'))
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features='html.parser')
        checkbox = soup.find(id='id_online')
        self.assertIn('checked', checkbox.attrs)
