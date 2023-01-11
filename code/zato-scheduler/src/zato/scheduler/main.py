# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# First thing in the process
from gevent import monkey
monkey.patch_all()

# stdlib
import os
from logging import captureWarnings, getLogger
from traceback import format_exc

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
try:
    import cloghandler # type: ignore
except ImportError:
    pass
else:
    cloghandler = cloghandler # For pyflakes

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems

# Zato
from zato.common.api import SCHEDULER
from zato.common.util.api import get_config, set_up_logging, store_pidfile
from zato.scheduler.server import Config, SchedulerServer

# ################################################################################################################################
# ################################################################################################################################

def main():

    if 'ZATO_SCHEDULER_BASE_DIR' in os.environ:
        os.chdir(os.environ['ZATO_SCHEDULER_BASE_DIR'])

    # Always attempt to store the PID file first
    store_pidfile(os.path.abspath('.'))

    # Capture warnings to log files
    captureWarnings(True)

    # Where we keep our configuration
    repo_location = os.path.join('.', 'config', 'repo')

    # Logging configuration
    set_up_logging(repo_location)

    # The main configuration object
    config = Config.from_repo_location(repo_location)

    logger = getLogger(__name__)
    logger.info('Scheduler starting (http{}://{}:{})'.format(
        's' if config.main.crypto.use_tls else '', config.main.bind.host, config.main.bind.port))

    # Reusable
    startup_jobs_config_file = 'startup_jobs.conf'

    # Fix up configuration so it uses the format that internal utilities expect
    for name, job_config in iteritems(get_config(repo_location, startup_jobs_config_file, needs_user_config=False)):

        # Ignore jobs that have been removed
        if name in SCHEDULER.JobsToIgnore:
            logger.info('Ignoring job `%s (%s)`', name, startup_jobs_config_file)
            continue

        job_config['name'] = name
        config.startup_jobs.append(job_config)

    # Run the scheduler server now
    try:
        SchedulerServer(config).serve_forever()
    except Exception:
        logger.warning(format_exc())

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
