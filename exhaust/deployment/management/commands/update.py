'''
A management command to deploy code changes to the live site.
'''
# We use posixpath because we want it to use Unix joining rules, rather than
# whatever is on the local system (not that I intend to use anything else).
import posixpath

import fabric
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        conf = settings.DEPLOYMENT

        # Make my fstrings a little less ugly.
        root_path = conf['ROOT_DIR']
        venv_path = posixpath.join(root_path, '.venv')
        venv_activate_path = posixpath.join(venv_path, 'bin/activate')
        requirements_path = posixpath.join(root_path, 'requirements.txt')
        managepy_path = posixpath.join(root_path, 'manage.py')

        connection = fabric.Connection(conf['HOST'], user=conf['SUDO_USER'])
        connection.sudo(f'git -C {conf["ROOT_DIR"]} pull', user=conf['USER'])

        # Nuke venv & rebuild.
        connection.sudo(f'rm -rf {venv_path}', user=conf['USER'])
        connection.sudo(f'virtualenv -p python3.8 {venv_path}', user=conf['USER'])
        # There's much of this "bash -c" stuff; it's unavoidable as we need to
        # include shell scripts that play with their env :(
        connection.sudo(f'bash -c "source {venv_activate_path} && pip install -r {requirements_path}"', user=conf['USER'])
        settings_file = conf['DJANGO_SETTINGS_MODULE']
        connection.sudo(f'bash -c "source {venv_activate_path} && {managepy_path} --noinput migrate --settings {settings_file}"', user=conf['USER'])
        connection.sudo(f'bash -c "source {venv_activate_path} && {managepy_path} --noinput remove_stale_contenttypes --settings {settings_file}"', user=conf['USER'])

        connection.sudo(f'bash -c "source ~/.nvm/nvm.sh && cd {root_path} && nvm install && nvm use && npm install -g yarn && yarn && yarn run build"', user=conf['USER'])
        connection.sudo(f'bash -c "source {venv_activate_path} && {managepy_path} collectstatic --noinput -l --settings {settings_file}"', user=conf['USER'])

        connection.sudo('service memcached restart')
        connection.sudo('supervisorctl restart all')
