from django.conf import settings
from django.core.management.base import BaseCommand

from .helpers import HelpfulConnection


class Command(BaseCommand):
    help = 'runs manage.py on the remote host with the given arguments'

    def add_arguments(self, parser):
        parser.add_argument('arguments', nargs='+', help='arguments to pass to manage.py')

    def handle(self, *args, **options):
        managepy_command = ' '.join(options['arguments'])
        conf = settings.DEPLOYMENT
        connection = HelpfulConnection(conf['HOST'], user=conf['SUDO_USER'])
        connection.run_managepy(managepy_command)
