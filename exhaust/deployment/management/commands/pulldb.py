import subprocess

import fabric
from django.conf import settings
from django.core.management.base import BaseCommand

from .helpers import make_db_backup


class Command(BaseCommand):
    help = 'imports a live database to your local database. This is a destructive operation!'

    def handle(self, *args, **options):
        conf = settings.DEPLOYMENT

        connection = fabric.Connection(conf['HOST'], user=conf['SUDO_USER'])

        local_db = conf['LOCAL_DATABASE_NAME']
        local_dump = make_db_backup(connection)

        subprocess.run(['dropdb', local_db], check=True)
        subprocess.run(['createdb', local_db], check=True)
        with open(local_dump) as fd:
            subprocess.run(['psql', '--quiet', local_db], stdin=fd, check=True)
