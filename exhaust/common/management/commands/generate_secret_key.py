from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = 'generates a new .secret_key file'

    def handle(self, *args, **options):
        with open(settings.SECRET_KEY_FILE, "w") as fd:
            fd.write(get_random_secret_key())
