import posixpath

import fabric
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'runs manage.py on the remote host with the given arguments'

    def add_arguments(self, parser):
        parser.add_argument('arguments', nargs='+', help='arguments to pass to manage.py')

    def handle(self, *args, **options):
        conf = settings.DEPLOYMENT

        root_path = conf['ROOT_DIR']
        venv_activate_path = posixpath.join(root_path, '.venv', 'bin/activate')
        managepy_path = posixpath.join(root_path, 'manage.py')
        settings_file = conf['DJANGO_SETTINGS_MODULE']
        managepy_command = ' '.join(options['arguments'])

        connection = fabric.Connection(conf['HOST'], user=conf['SUDO_USER'])
        connection.sudo(f'bash -c "source {venv_activate_path} && {managepy_path} {managepy_command} --settings {settings_file}"', user=conf['USER'])
