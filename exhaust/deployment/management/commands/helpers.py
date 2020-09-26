import os
import posixpath

from django.conf import settings
from django.utils.timezone import now
from fabric import Connection


class HelpfulConnection(Connection):
    '''
    This is a terrible name for a class. But it's a subclass of
    fabric.Connection with some useful helpers for running things in a virtual
    environment & running management commands.

    This makes it easier to see in the source what we're trying to *do*,
    rather than what is bein run; it gets so drowned out in sudo/venv
    activation/settings noise.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        conf = settings.DEPLOYMENT
        self.venv_user = conf['USER']
        self.venv_activate_path = posixpath.join(conf['ROOT_DIR'], '.venv', 'bin/activate')
        self.managepy_path = posixpath.join(conf['ROOT_DIR'], 'manage.py')
        self.settings_file = conf['DJANGO_SETTINGS_MODULE']

    def run_in_venv(self, command):
        self.sudo(f'bash -c "source {self.venv_activate_path} && {command}"', user=self.venv_user)

    def run_managepy(self, command):
        self.run_in_venv(f'{self.managepy_path} {command} --settings {self.settings_file}')


def make_db_backup(connection):
    '''Backs up the database on the remote site using the given
    fabric.Connnection instance `connection`.

    Returns the filename of the local file that was created. My convention
    is ~/backups/DB_NAME/DB_NAME-TIMESTAMP.sql'
    '''

    conf = settings.DEPLOYMENT
    user = conf['USER']
    db_name = conf['DATABASE_NAME']
    remote_db_dump_path = posixpath.join('/home/', conf['USER'], f'{conf["DATABASE_NAME"]}.sql')
    local_backup_dir = os.path.expanduser(os.path.join('~/', 'Backups', db_name))
    local_backup_file = os.path.join(local_backup_dir, f'{db_name}-{now().isoformat()}.sql')

    try:
        os.makedirs(local_backup_dir)
    except FileExistsError:
        # this is fine :)
        pass

    connection.sudo(f'su - {user} -c "pg_dump {db_name} -cOx -f {remote_db_dump_path} --clean"')
    connection.get(remote_db_dump_path, local_backup_file)
    connection.sudo(f'rm -f {remote_db_dump_path}')

    return local_backup_file
