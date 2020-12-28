#!/usr/bin/env python
import os
import pwd
import sys
import warnings

from django.core.management import execute_from_command_line


def main():
    warnings.simplefilter('module')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exhaust.settings.local')
    os.environ.setdefault('DB_USER', pwd.getpwuid(os.getuid()).pw_name)
    os.environ.setdefault('DB_NAME', 'exhaust')
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
