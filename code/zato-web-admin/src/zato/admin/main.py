# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
try:
    import cloghandler # type: ignore
except ImportError:
    pass
else:
    cloghandler = cloghandler # For pyflakes

# stdlib
import logging
import os

# MySQL
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Django
import django
from django.core.management import call_command, execute_from_command_line

# Zato
from zato.admin.zato_settings import update_globals
from zato.common.json_internal import loads
from zato.common.repo import RepoManager
from zato.common.util.api import store_pidfile
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Currently, this is not needed.
needs_migrate = True

# ################################################################################################################################
# ################################################################################################################################

def update_password(base_dir:'str') -> 'None':

    # stdlib
    import sys # type: ignore
    from json import loads

    # Obtain a full path to an optional file with credentials
    file_dir  = os.path.join(base_dir, '..')
    file_dir  = os.path.abspath(file_dir)
    file_path = os.path.join(file_dir, 'env.json')

    # First, ensure that the optional file with credentials exists at all
    if not os.path.exists(file_path):
        return

    # .. extract the underlying details ..
    data = open(file_path).read()
    data = loads(data)
    password = data.get('dashboard_password')

    # .. make sure we have a password for the user ..
    if not password:
        return

    # At this point, we have all the information required to change the password

    # Build a full path to the main Zato command
    bin_dir = os.path.dirname(sys.executable)
    zato_cmd = os.path.join(bin_dir, 'zato')

    # .. build the command to use ..
    command = f'{zato_cmd} update password {base_dir} admin --password {password}'

    # .. and do run it.
    _ = os.system(command)

# ################################################################################################################################
# ################################################################################################################################

def main():

    # stdlib
    import sys

    # Zato
    from zato.common.util.api import parse_cmd_line_options
    from zato.common.util.env import populate_environment_from_file

    cmd_line_options = sys.argv[1]
    cmd_line_options = parse_cmd_line_options(cmd_line_options)

    env_file = cmd_line_options.get('env_file') or ''
    _ = populate_environment_from_file(env_file)

    env_dir = os.environ.get('ZATO_DASHBOARD_BASE_DIR')

    base_dir = env_dir or '.'
    base_dir_abs = os.path.abspath(base_dir)

    store_pidfile(base_dir_abs)
    repo_dir = os.path.join(base_dir, 'config', 'repo')

    # Update Django settings
    config = loads(open_r(os.path.join(repo_dir, 'web-admin.conf')).read())
    config['config_dir'] = base_dir_abs

    if env_dir:
        log_config = config['log_config']
        log_config = os.path.join(env_dir, log_config)
        config['log_config'] = log_config

    # Load our configuration for Django
    update_globals(config)

    # Initialize Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
    django.setup()

    # Optionally, reset the admin user's password
    try:
        update_password(base_dir_abs)
    except Exception as e:
        logger.info('Exception caught: %s', e)

    # Optionally, run internal Django migrations
    if needs_migrate:
        _ = call_command('migrate', verbosity=999, fake=True)

    # Load our initial data
    _ = call_command('loaddata', os.path.join(repo_dir, 'initial-data.json'))

    RepoManager(repo_dir).ensure_repo_consistency()
    execute_from_command_line([
        'zato-web-admin',
        'runserver',
        '--noreload',
        '--nothreading',
        '--skip-checks',
        '{host}:{port}'.format(**config)
    ])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
