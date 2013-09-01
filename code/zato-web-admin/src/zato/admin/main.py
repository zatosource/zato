# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# stdlib
import json, os
from logging import getLogger
from wsgiref.simple_server import make_server

# Django
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command

# Zato
from zato.admin.zato_settings import update_globals
from zato.common.repo import RepoManager

logger = getLogger(__name__)

def main():
    
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

    app = WSGIHandler()
    make_server(config['host'], config['port'], app).serve_forever()

if __name__ == '__main__':
    main()
