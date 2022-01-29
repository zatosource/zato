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

# Zato
from zato.common.odb.query.cleanup import get_subscriptions
from zato.common.util.api import set_up_logging
from zato.common.util.time_ import datetime_to_ms

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

    def _get_subscriptions(self, now:'datetime', max_hours_not_interacted:'int') -> 'anylist':

        # Turn hours into a UNIX time object, as expected by the database
        max_last_interaction_time = now - timedelta(hours=max_hours_not_interacted)
        max_last_interaction_time = datetime_to_ms(max_last_interaction_time)

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_subscriptions(session, max_last_interaction_time)
            return result

# ################################################################################################################################

    def cleanup_pub_sub(self):

        # Start of our cleanup procedure
        now = datetime.utcnow()

        # Find all subscribers that did not interact with us for at least that many hours
        max_hours_not_interacted = 24

        subs = self._get_subscriptions(now, max_hours_not_interacted)
        print(111, subs)

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

    # Path to the scheduler's configuration file will be the first argument
    # that we are invoked with.
    repo_location = sys.argv[1] # type: str
    repo_location = os.path.expanduser(repo_location)

    run_cleanup(repo_location)

# ################################################################################################################################
# ################################################################################################################################
