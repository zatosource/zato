# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# stdlib
import json, os

# Django
from django.core.management import call_command, execute_manager

# Zato
from zato.admin.zato_settings import update_globals
from zato.common.repo import RepoManager
from zato.common.util import store_pidfile

def main():
    store_pidfile(os.path.abspath('.'))
    repo_dir = os.path.join('.', 'config', 'repo')

    # Update Django settings
    config = json.loads(open(os.path.join(repo_dir, 'web-admin.conf')).read())
    config['config_dir'] = os.path.abspath('.')
    update_globals(config)

    # Store the PID so that the server can be later stopped by its PID.
    open('./.web-admin.pid', 'w').write(str(os.getpid()))

    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
    call_command('loaddata', os.path.join(repo_dir, 'initial-data.json'))

    RepoManager(repo_dir).ensure_repo_consistency()

    # Cannot be imported before update_globals does its job of updating settings' configuration
    from zato.admin import settings

    execute_manager(settings, ['zato-web-admin', 'runserver', '--noreload', '{host}:{port}'.format(**config)])

if __name__ == '__main__':
    main()
