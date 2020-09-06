import fabric
from django.conf import settings
from django.core.management.base import BaseCommand

from .helpers import make_db_backup


class Command(BaseCommand):
    help = 'Creates a backup of the live database to a local file in ~/Backups'

    def handle(self, *args, **options):
        conf = settings.DEPLOYMENT
        connection = fabric.Connection(conf['HOST'], user=conf['SUDO_USER'])
        filename = make_db_backup(connection)
        self.stdout.write(f'Backup saved to {filename} ')
