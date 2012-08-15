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
import os, sys
import logging.config

# psycopg2
import psycopg2

# Zato
from zato.common.util import get_app_context, get_config, get_crypto_manager, TRACE1

def run(host, port, base_dir, start_singleton):

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
    parallel_server.crypto_manager = crypto_manager
    parallel_server.odb_data = config.odb
    parallel_server.host = host
    parallel_server.port = port
    parallel_server.repo_location = repo_location
    parallel_server.base_dir = base_dir
    parallel_server.fs_server_config = config
    parallel_server.stats_jobs = app_context.get_object('stats_jobs')

    '''work_dir = config.hot_deploy.work_dir
    if not os.path.isabs(work_dir):
        work_dir = os.path.abspath(os.path.join(repo_location, work_dir))

    parallel_server.work_dir = work_dir'''

    pickup_dir = config.hot_deploy.pickup_dir
    if not os.path.isabs(pickup_dir):
        pickup_dir = os.path.join(repo_location, pickup_dir)

    pickup = app_context.get_object('pickup')
    pickup.pickup_dir = pickup_dir
    pickup.pickup_event_processor.pickup_dir = pickup_dir

    if start_singleton:
        singleton_server = app_context.get_object('singleton_server')
        singleton_server.initial_sleep_time = int(config.singleton.initial_sleep_time) / 1000.
        parallel_server.singleton_server = singleton_server

        # Wow, this line looks weird. What it does is simply assigning a parallel
        # server instance to the singleton server.
        parallel_server.singleton_server.parallel_server = parallel_server

    parallel_server.after_init()
    parallel_server.run_forever()

if __name__ == '__main__':
    host, port, base_dir = sys.argv[1:4]
    start_singleton = True if len(sys.argv) >= 5 else False
    run(host, int(port), base_dir, start_singleton)
