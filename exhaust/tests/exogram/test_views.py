from datetime import datetime

from bs4 import BeautifulSoup
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import make_aware

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
class GramViewsTestCase(TestCase):
    def test_gram_view_disabled_for_non_admins(self):
        """
        Ensure that `exogram` views are only visible to me, for now. When this
        goes live and can be removed, all the lines in the other tests that
        create & log in a user can be deleted too.
        """
        response = self.client.get(reverse('exogram:gram_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIs(response['Location'].startswith(reverse('admin:login')), True)

    def test_gram_list_view(self):
        self.client.force_login(UserFactory.create(is_staff=True, is_superuser=True))

        gram = GramFactory.create(image='small-image.jpg')

        response = self.client.get(reverse('exogram:gram_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context_data['object_list']), [gram])

    def test_gram_detail_view(self):
        self.client.force_login(UserFactory.create(is_staff=True, is_superuser=True))

        gram = GramFactory.create(image='small-image.jpg')

        # Simple tests of various branches in the template.
        response = self.client.get(gram.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # Test the branch with Markdown text.
        gram = GramFactory.create(image='small-image.jpg', text='_Testing!_')
        response = self.client.get(gram.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features='html.parser')
        markdown = soup.find(attrs={'class': 'markdown--centered'}).decode_contents().strip()
        self.assertEqual(markdown, '<p><em>Testing!</em></p>')

        # Test the branch with Markdown text.
        gram = GramFactory.create(image='small-image.jpg', commons_link='https://commons.wikimedia.org/xxxx')
        response = self.client.get(gram.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, features='html.parser')
        link_tag = soup.find(attrs={'class': 'exogram-detail__commons'}).find('a')
        self.assertEqual(link_tag['href'], gram.commons_link)

    def test_gram_detail_view_prevnext(self):
        '''
        Test branches for newer/older in the template.
        '''
        self.client.force_login(UserFactory.create(is_staff=True, is_superuser=True))
        oldest = GramFactory.create(image='small-image.jpg', date=make_aware(datetime(year=2000, month=1, day=1)))
        older = GramFactory.create(image='small-image.jpg', date=make_aware(datetime(year=2000, month=1, day=2)))
        current = GramFactory.create(image='small-image.jpg', date=make_aware(datetime(year=2000, month=1, day=3)))

        # Tuples of (object_to_get, expected_to_be_older, expected_to_be_newer)
        tests = [
            (oldest, None, older),
            (older, oldest, current),
            (current, older, None),
        ]

        for obj, expect_older, expect_newer in tests:
            response = self.client.get(obj.get_absolute_url())
            self.assertEqual(response.status_code, 200)
            soup = BeautifulSoup(response.content, features='html.parser')
            if expect_older is not None:
                link = soup.find(attrs={'class': 'paginator__item--previous'}).find('a')
                self.assertEqual(link['href'], expect_older.get_absolute_url())

            if expect_newer is not None:
                link = soup.find(attrs={'class': 'paginator__item--next'}).find('a')
                self.assertEqual(link['href'], expect_newer.get_absolute_url())

    def test_gram_not_found_is_404(self):
        '''
        Ensure that the not found page for gram_detail gives a 404.
        '''
        self.client.force_login(UserFactory.create(is_staff=True, is_superuser=True))
        response = self.client.get(reverse('exogram:gram_detail', kwargs={'public_id': 'notexist'}))
        self.assertEqual(response.status_code, 404)
