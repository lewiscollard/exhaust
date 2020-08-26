'''
A management command to deploy code changes to the live site.

Heavily inspired by the onespacemedia-server-management command:
https://github.com/onespacemedia/server-management/blob/develop/server_management/management/commands/update.py

Rewritten entirely to use a modern Fabric and to remove cleverness around venv
(a small amount of downtime during deploys is OK for me).
'''
import fabric
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        conf = settings.DEPLOYMENT

        connection = fabric.Connection(conf['HOST'], user=conf['SUDO_USER'])
        connection.sudo('ls', user=conf['USER'])

        self.sudo_cd(connection, conf['ROOT_DIR'], 'git pull', user=conf['USER'])
        # Build frontend stuff.
        self.sudo_cd(connection, conf['ROOT_DIR'], '. ~/.nvm/nvm.sh && nvm install && yarn && yarn run build', user=conf['USER'])
        # Nuke venv & rebuild.
        self.sudo_cd(connection, conf['ROOT_DIR'], 'rm -rf .venv', user=conf['USER'])
        self.sudo_cd(connection, conf['ROOT_DIR'], 'virtualenv -p python3.8 .venv', user=conf['USER'])
        self.sudo_cd(connection, conf['ROOT_DIR'], 'source .venv/bin/activate && pip install -r requirements.txt', user=conf['USER'])
        settings_file = conf['DJANGO_SETTINGS_MODULE']
        # Collect static files and migrate DB.
        self.sudo_cd(connection, conf['ROOT_DIR'], f'source .venv/bin/activate && ./manage.py collectstatic --noinput -l --settings {settings_file}', user=conf['USER'])
        self.sudo_cd(connection, conf['ROOT_DIR'], f'source .venv/bin/activate && echo yes yes | ./manage.py migrate --settings {settings_file}', user=conf['USER'])

        connection.sudo('service memcached restart')
        connection.sudo('supervisorctl restart all')

    def sudo_cd(self, connection, path, command, user=None, **kwargs):
        # Workaround (and not a nice one) for a bug in invoke wherein you
        # can't use the sudo *and* cd context managers.
        # https://github.com/pyinvoke/invoke/issues/459
        user = user or 'root'
        connection.sudo(f'bash -c "cd {path} && {command}"', user=user, **kwargs)
