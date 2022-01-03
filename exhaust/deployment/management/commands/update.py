'''
A management command to deploy code changes to the live site.
'''
# We use posixpath because we want it to use Unix joining rules, rather than
# whatever is on the local system (not that I intend to use anything else).
import posixpath

from django.conf import settings
from django.core.management.base import BaseCommand

from .helpers import HelpfulConnection


class Command(BaseCommand):
    def handle(self, *args, **options):
        conf = settings.DEPLOYMENT

        # Make my fstrings a little less ugly.
        root_path = conf['ROOT_DIR']
        venv_path = posixpath.join(root_path, '.venv')
        requirements_path = posixpath.join(root_path, 'requirements.txt')
        pip_constraint_file = posixpath.join(root_path, 'pip.txt')

        connection = HelpfulConnection(conf['HOST'], user=conf['SUDO_USER'])
        connection.sudo(f'git -C {conf["ROOT_DIR"]} pull', user=conf['USER'])

        # Nuke venv & rebuild.
        connection.sudo(f'rm -rf {venv_path}', user=conf['USER'])
        connection.sudo(f'virtualenv -p python3.8 {venv_path}', user=conf['USER'])
        connection.run_in_venv(f'pip install --upgrade pip -c {pip_constraint_file}')
        connection.run_in_venv(f'pip install -r {requirements_path}')
        connection.run_managepy('migrate --noinput')
        connection.run_managepy('remove_stale_contenttypes --noinput')

        connection.sudo(f'bash -c "source ~/.nvm/nvm.sh && cd {root_path} && nvm install && nvm use && npm install -g yarn && yarn && yarn run build"', user=conf['USER'])
        connection.run_managepy('collectstatic --noinput -l')

        connection.sudo('service memcached restart')
        connection.sudo('supervisorctl restart all')
        # In case I've broken the nginx config; this should cause nginx to
        # keep running (at least until the next reboot) while causing the
        # update to fail.
        connection.sudo('nginx -t')
        connection.sudo('service nginx reload')
