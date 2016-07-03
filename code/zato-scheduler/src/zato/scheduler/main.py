# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

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

# Zato
from zato.common.util import absolutize_path, get_config, store_pidfile
from zato.scheduler.server import SchedulerServer

def main():

    # Always attempt to store the PID file first
    store_pidfile(os.path.abspath('.'))

    # Capture warnings to log files
    logging.captureWarnings(True)

    repo_location = os.path.join('.', 'config', 'repo')

    # Logging configuration
    with open(os.path.join(repo_location, 'logging.conf')) as f:
        dictConfig(yaml.load(f))

    # Read config in and make paths absolute
    conf = get_config(repo_location, 'scheduler.conf')

    if conf.crypto.use_tls:
        conf.crypto.ca_certs_location = absolutize_path(repo_location, conf.crypto.ca_certs_location)
        conf.crypto.priv_key_location = absolutize_path(repo_location, conf.crypto.priv_key_location)
        conf.crypto.cert_location = absolutize_path(repo_location, conf.crypto.cert_location)

    logger = logging.getLogger(__name__)
    logger.info('Scheduler starting (http{}://{}:{})'.format(
        's' if conf.crypto.use_tls else '', conf.bind.host, conf.bind.port))

    # Run the scheduler server
    try:
        SchedulerServer(conf).serve_forever()
    except Exception, e:
        logger.warn(format_exc(e))

if __name__ == '__main__':
    main()
