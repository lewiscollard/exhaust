import os
import subprocess  # nosec

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'rsyncs media files from the remote host'

    def handle(self, *args, **options):
        conf = settings.DEPLOYMENT

        try:
            os.makedirs(settings.MEDIA_ROOT)
        except FileExistsError:
            # this will almost always be the case :)
            pass

        subprocess.run(  # nosec
            [
                'rsync',
                '--progress',
                '-av',
                f'{conf["SUDO_USER"]}@{conf["HOST"]}:{conf["MEDIA_DIR"]}',
                settings.MEDIA_ROOT
            ], check=True
        )
