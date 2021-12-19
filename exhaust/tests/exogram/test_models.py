from datetime import datetime

from django.test import TestCase, override_settings
from django.utils.timezone import make_aware

from exhaust.tests.factories import GramFactory


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
class GramTestCase(TestCase):
    def test_gram_str(self):
        date = make_aware(datetime(year=2000, month=1, day=1))
        gram = GramFactory.create(image='small-image.jpg', date=date)
        self.assertEqual(str(gram), '2000-01-01')

        gram = GramFactory.create(image='small-image.jpg', text='Test', date=date)
        self.assertEqual(str(gram), '2000-01-01: Test')

        gram = GramFactory.create(image='small-image.jpg', text=('X' * 61), date=date)
        self.assertEqual(str(gram), f'2000-01-01: {"X" * 57}...')

    def test_gram_save(self):
        # Test both the create-public-id and implied "else" branch.
        gram = GramFactory.create(image='small-image.jpg')
        gram_id = gram.public_id
        self.assertGreater(len(gram_id), 6)

        gram.save()
        self.assertEqual(gram.public_id, gram_id)

    def test_gram_get_absolute_url(self):
        gram = GramFactory.create(image='small-image.jpg', public_id='TEST1234')
        self.assertEqual(gram.get_absolute_url(), '/exogram/TEST1234/')

        gram.slug = 'i-has-a-slug'
        self.assertEqual(gram.get_absolute_url(), '/exogram/TEST1234/i-has-a-slug/')

    def test_gram_factory_detail_pagination(self):
        oldest = GramFactory.create(image='small-image.jpg', date=make_aware(datetime(year=2000, month=1, day=1)))
        older = GramFactory.create(image='small-image.jpg', date=make_aware(datetime(year=2000, month=1, day=2)))
        current = GramFactory.create(image='small-image.jpg', date=make_aware(datetime(year=2000, month=1, day=3)))

        self.assertEqual(oldest.detail_pagination(), {
            'newer': older.get_absolute_url(),
            'older': None,
        })

        self.assertEqual(older.detail_pagination(), {
            'older': oldest.get_absolute_url(),
            'newer': current.get_absolute_url(),
        })

        self.assertEqual(current.detail_pagination(), {
            'older': older.get_absolute_url(),
            'newer': None,
        })
