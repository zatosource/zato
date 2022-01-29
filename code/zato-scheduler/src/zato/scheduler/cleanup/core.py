# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# This needs to be done as soon as possible
from gevent.monkey import patch_all
patch_all()

# Check comments in zato-server's main.py for why it is needed here
import cloghandler
cloghandler = cloghandler # For pyflakes

# stdlib
import os
from contextlib import closing
from datetime import datetime, timedelta
from logging import captureWarnings, getLogger

# Tabulate
from tabulate import tabulate

# Zato
from zato.common.odb.query.cleanup import get_subscriptions
from zato.common.util.api import set_up_logging, tabulate_dictlist
from zato.common.util.time_ import datetime_from_ms, datetime_to_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist
    from zato.scheduler.server import Config
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

class CleanupManager:
    logger:        'Logger'
    config:        'Config'
    repo_location: 'str'

    def __init__(self, repo_location:'str') -> 'None':
        self.repo_location = repo_location

# ################################################################################################################################

    def init(self):

        # Zato
        from zato.scheduler.server import Config

        # Make sure we are in the same directory that the scheduler is in
        base_dir = os.path.join(self.repo_location, '..', '..')
        base_dir = os.path.abspath(base_dir)
        os.chdir(base_dir)

        # Build our main configuration object
        self.config = Config.from_repo_location(self.repo_location)

        # Capture warnings to log files
        captureWarnings(True)

        # Logging configuration
        set_up_logging(self.repo_location)

        # Build our logger
        self.logger = getLogger(__name__)

# ################################################################################################################################

    def _get_subscriptions(self, now:'datetime', delta_not_interacted:'int') -> 'anylist':

        # Turn hours into a UNIX time object, as expected by the database
        max_last_interaction_time_dt = now - timedelta(hours=delta_not_interacted)
        max_last_interaction_time = datetime_to_ms(max_last_interaction_time_dt)

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_subscriptions(session, max_last_interaction_time)

        result = [elem._asdict() for elem in result]

        for elem in result:
            for key, value in elem.items():
                if key == 'last_interaction_time':
                    if not value:
                        value = '---'
                    else:
                        value = datetime_from_ms(value * 1000) # type: ignore
                elem[key] = value # type: ignore

        len_result = len(result)
        suffix = ' ' if len_result == 1 else 's '

        self.logger.info('Returning %s subscription%swith last interaction older than %s (delta: %s hours)',
            len_result, suffix, max_last_interaction_time_dt, delta_not_interacted)

        table = tabulate_dictlist(result)
        self.logger.info('** Subscriptions to clean up **\n%s', table)

        return result

# ################################################################################################################################

    def _cleanup_queue_by_sub_key(self, sub_key:'str') -> 'None':

# ################################################################################################################################

    def cleanup_pub_sub(self):

        # Start of our cleanup procedure
        now = datetime.utcnow()

        # Find all subscribers that did not interact with us for at least that many hours
        delta_not_interacted = 24


        subs = self._get_subscriptions(now, delta_not_interacted)



# ################################################################################################################################

    def run(self):

        # Clean up old pub/sub objects
        self.cleanup_pub_sub()

# ################################################################################################################################
# ################################################################################################################################

def run_cleanup(repo_location:'str'):

    # Build and initialize object responsible for cleanup tasks ..
    cleanup_manager = CleanupManager(repo_location)
    cleanup_manager.init()

    # .. if we are here, it means that we can start our work.
    cleanup_manager.run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import sys

    # Path to the scheduler's configuration file will be the first argument that we are invoked with,
    # unless we have an environment key that points to the scheduler's location.

    base_dir = os.environ.get('ZATO_SCHEDULER_BASE_DIR')

    if base_dir:
        repo_location = os.path.join(base_dir, 'config', 'repo')
    else:
        repo_location = sys.argv[1] # type: str

    repo_location = os.path.expanduser(repo_location)
    repo_location = os.path.abspath(repo_location)

    run_cleanup(repo_location)

# ################################################################################################################################
# ################################################################################################################################
