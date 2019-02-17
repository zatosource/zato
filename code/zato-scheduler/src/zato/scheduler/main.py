# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# First thing in the process
from gevent import monkey
monkey.patch_all()

# stdlib
import logging
import os
from logging.config import dictConfig
from traceback import format_exc

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
import cloghandler
cloghandler = cloghandler # For pyflakes

# YAML
import yaml

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common.util import absjoin, get_config, store_pidfile
from zato.scheduler.server import Config, SchedulerServer

# ################################################################################################################################

def main():

    # Always attempt to store the PID file first
    store_pidfile(os.path.abspath('.'))

    # Capture warnings to log files
    logging.captureWarnings(True)

    config = Config()
    repo_location = os.path.join('.', 'config', 'repo')

    # Logging configuration
    with open(os.path.join(repo_location, 'logging.conf')) as f:
        dictConfig(yaml.load(f))

    # Read config in and extend it with ODB-specific information
    config.main = get_config(repo_location, 'scheduler.conf')
    config.main.odb.fs_sql_config = get_config(repo_location, 'sql.conf', needs_user_config=False)

    # Make all paths absolute
    if config.main.crypto.use_tls:
        config.main.crypto.ca_certs_location = absjoin(repo_location, config.main.crypto.ca_certs_location)
        config.main.crypto.priv_key_location = absjoin(repo_location, config.main.crypto.priv_key_location)
        config.main.crypto.cert_location = absjoin(repo_location, config.main.crypto.cert_location)

    logger = logging.getLogger(__name__)
    logger.info('Scheduler starting (http{}://{}:{})'.format(
        's' if config.main.crypto.use_tls else '', config.main.bind.host, config.main.bind.port))

    # Fix up configuration so it uses the format internal utilities expect
    for name, job_config in iteritems(get_config(repo_location, 'startup_jobs.conf', needs_user_config=False)):
        job_config['name'] = name
        config.startup_jobs.append(job_config)

    # Run the scheduler server
    try:
        SchedulerServer(config, repo_location).serve_forever()
    except Exception:
        logger.warn(format_exc())

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
