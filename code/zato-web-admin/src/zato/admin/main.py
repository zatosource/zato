# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler
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

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')

logger = logging.getLogger(__name__)

def main():

    # stdlib
    import sys

    # Zato
    from zato.common.util.api import parse_cmd_line_options
    from zato.common.util.env import populate_environment_from_file

    cmd_line_options = sys.argv[1]
    cmd_line_options = parse_cmd_line_options(cmd_line_options)

    env_file = cmd_line_options.get('env_file') or ''
    populate_environment_from_file(env_file)

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

    update_globals(config)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

    django.setup()

    call_command('migrate')
    call_command('loaddata', os.path.join(repo_dir, 'initial-data.json'))

    RepoManager(repo_dir).ensure_repo_consistency()
    execute_from_command_line(['zato-web-admin', 'runserver', '--noreload', '--nothreading', '{host}:{port}'.format(**config)])

if __name__ == '__main__':
    main()
