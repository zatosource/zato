# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import json, os
from logging import getLogger
from wsgiref.simple_server import make_server

# Django
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from django.core.servers.basehttp import AdminMediaHandler

# Zato
from zato.admin.zato_settings import update_globals
from zato.common.repo import RepoManager

logger = getLogger(__name__)

def main():
    
    repo_dir = os.path.join('.', 'config', 'repo')
    
    # Update Django settings
    config = json.loads(open(os.path.join(repo_dir, 'zato-admin.conf')).read())
    config['config_dir'] = os.path.abspath('.')
    update_globals(config)
    
    # Store the PID so that the server can be later stopped by its PID.
    open('./.zato-admin.pid', 'w').write(str(os.getpid()))
        
    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
    call_command('loaddata', os.path.join(repo_dir, 'initial-data.json'))
    
    RepoManager(repo_dir).ensure_repo_consistency()

    app = WSGIHandler()
    make_server(config['host'], config['port'], app).serve_forever()

if __name__ == '__main__':
    main()
