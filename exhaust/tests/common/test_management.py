import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase


class ManagementCommandsTestCase(TestCase):
    def test_generating_secret_key_works(self):
        if os.path.exists(settings.SECRET_KEY_FILE):
            os.unlink(settings.SECRET_KEY_FILE)

        # sanity check
        self.assertFalse(os.path.exists(settings.SECRET_KEY_FILE))

        call_command('generate_secret_key')

        self.assertTrue(os.path.exists(settings.SECRET_KEY_FILE))
        with open(settings.SECRET_KEY_FILE) as fd:
            self.assertEqual(len(fd.read().strip()), 50)
