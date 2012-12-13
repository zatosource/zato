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

# Setting the custom logger must come first
import logging
from zato.server.log import ZatoLogger
logging.setLoggerClass(ZatoLogger)

logging.captureWarnings(True)

# stdlib
import glob, os, sys
import logging.config
from threading import currentThread

# gunicorn
from gunicorn.app.base import Application

# psycopg2
import psycopg2

# Zato
from zato.common import KVDB
from zato.common.repo import RepoManager
from zato.common.util import clear_locks, get_app_context, get_config, get_crypto_manager, TRACE1
from zato.server.pickup import get_pickup

class ZatoGunicornApplication(Application):
    def __init__(self, zato_wsgi_app, config_main, *args, **kwargs):
        self.zato_wsgi_app = zato_wsgi_app
        self.config_main = config_main
        self.zato_host = None
        self.zato_port = None
        self.zato_config = {}
        super(ZatoGunicornApplication, self).__init__(*args, **kwargs)
        
    def init(self, *ignored_args, **ignored_kwargs):
        self.cfg.set('post_fork', self.zato_wsgi_app.post_fork) # Initializes a worker
        self.cfg.set('on_starting', self.zato_wsgi_app.on_starting) # Generates the deployment key
        
        for k, v in self.config_main.items():
            if k.startswith('gunicorn') and v:
                k = k.replace('gunicorn_', '')
                if k == 'bind':
                    if not ':' in v:
                        raise ValueError('No port found in main.gunicorn_bind [{v}]; a proper value is, for instance, [{v}:17010]'.format(v=v))
                    else:
                        host, port = v.split(':')
                        self.zato_host = host
                        self.zato_port = port
                self.cfg.set(k, v)
            else:
                if 'deployment_lock' in k:
                    v = int(v)
                    
                self.zato_config[k] = v
                
        for name in('deployment_lock_expires', 'deployment_lock_timeout'):
            setattr(self.zato_wsgi_app, name, self.zato_config[name])
            
        self.zato_wsgi_app.has_gevent = 'gevent' in self.cfg.settings['worker_class'].value
        
    def load(self):
        return self.zato_wsgi_app.on_wsgi_request

def run(base_dir):

    os.chdir(base_dir)
    
    # We're doing it here even if someone doesn't use PostgreSQL at all
    # so we're not suprised when someone suddenly starts using PG.
    # TODO: Make sure it's registered for each of the subprocess when the code's
    #       finally modified to use subprocesses.
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

    repo_location = os.path.join(base_dir, 'config', 'repo')

    # Configure the logging first, before configuring the actual server.
    logging.addLevelName('TRACE1', TRACE1)
    logging.config.fileConfig(os.path.join(repo_location, 'logging.conf'))

    config = get_config(repo_location, 'server.conf')
    app_context = get_app_context(config)

    crypto_manager = get_crypto_manager(repo_location, app_context, config)
    parallel_server = app_context.get_object('parallel_server')
    
    zato_gunicorn_app = ZatoGunicornApplication(parallel_server, config.main)
    
    #pickup = get_pickup('gevent' in zato_gunicorn_app.cfg.settings['worker_class'].value)
    
    parallel_server.crypto_manager = crypto_manager
    parallel_server.odb_data = config.odb
    parallel_server.host = zato_gunicorn_app.zato_host
    parallel_server.port = zato_gunicorn_app.zato_port
    parallel_server.repo_location = repo_location
    parallel_server.base_dir = base_dir
    parallel_server.fs_server_config = config
    parallel_server.stats_jobs = app_context.get_object('stats_jobs')
    parallel_server.app_context = app_context

    pickup_dir = config.hot_deploy.pickup_dir
    if not os.path.isabs(pickup_dir):
        pickup_dir = os.path.join(repo_location, pickup_dir)

    #pickup.pickup_dir = pickup_dir
    #pickup.pickup_event_processor.pickup_dir = pickup_dir

    # Remove all locks possibly left over by previous server instances
    clear_locks(app_context.get_object('kvdb'), config.main.token, config.kvdb, crypto_manager.decrypt)
        
    # Turn the repo dir into an actual repository and commit any new/modified files
    RepoManager(repo_location).ensure_repo_consistency()

    # Run the app at last
    zato_gunicorn_app.run()
 
if __name__ == '__main__':
    base_dir = sys.argv[1]
    run(base_dir)
