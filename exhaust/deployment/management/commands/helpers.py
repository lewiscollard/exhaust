import os
import posixpath

from django.conf import settings
from django.utils.timezone import now


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
