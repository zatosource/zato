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
from zato.common.odb.query.pubsub.delivery import get_sql_msg_ids_by_sub_key
from zato.common.util.api import grouper, set_up_logging, tabulate_dictlist
from zato.common.util.time_ import datetime_from_ms, datetime_to_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, dictlist, stranydict
    from zato.scheduler.server import Config
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

class MaxLast:
    as_float:    'float'
    as_datetime: 'datetime'

# ################################################################################################################################
# ################################################################################################################################

class Config:
    DeltaNotInteracted = 24 # In hours
    MsgDeleteBatchSize = 2

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

    def _get_suffix(self, items:'any_', needs_space:'bool'=True) -> 'str':
        len_out = len(items)
        suffix = '' if len_out == 1 else 's'
        if needs_space:
            suffix += ' '
        return suffix

# ################################################################################################################################

    def _get_subscriptions(self, max_last:'MaxLast', delta_not_interacted:'int') -> 'anylist':

        '''
        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_subscriptions(session, max_last.as_float)

        # Convert SQL results to a dict that we can easily work with
        result = [elem._asdict() for elem in result]

        # This is what we will return. We need a new dict because we are adding
        # a new columns and we what to preserve the insertion order.
        out = []

        for idx, elem in enumerate(result, 1):
            out_elem = {
                'idx': idx,
            }
            for key, value in elem.items():
                if key in ('last_interaction_time', 'ext_client_id'):
                    if not value:
                        value = '---'
                    else:
                        if key == 'last_interaction_time':
                            value = datetime_from_ms(value * 1000) # type: ignore
                elem[key] = value # type: ignore

            out_elem.update(elem)
            out.append(out_elem)
        '''

        out = out[:1]
        print(out)

        suffix = self._get_suffix(out)

        self.logger.info('CLEANSUB: Returning %s subscription%swith last interaction older than %s (delta: %s hours)',
            len(out), suffix, max_last.as_datetime, delta_not_interacted)

        table = tabulate_dictlist(out)
        self.logger.info('CLEANSUB: ** Subscriptions to clean up **\n%s', table)

        return out

# ################################################################################################################################

    def _cleanup_msg_group(self, sub_key:'str', msg_group:'dictlist') -> 'None':

        batch_size = Config.MsgDeleteBatchSize

        split = grouper(batch_size, msg_group)
        split = list(split)
        len_split = len(split)

        suffix = self._get_suffix(split, needs_space=False)
        self.logger.info('CLEANSUB: Message(s) for `%s` turned into %s group%s, batch_size:%s',
            sub_key, len_split, suffix, batch_size)

# ################################################################################################################################

    def _cleanup_sub(self, max_last:'MaxLast', sub:'stranydict') -> 'None':

        # Local aliases
        sub_key = sub['sub_key']

        self.logger.info('CLEANSUB: ---------------')
        self.logger.info('CLEANSUB: Looking up queue messages for %s', sub_key)

        # We look up all the messages in the database which is why the last_sql_run
        # needs to be set to a value that will be always matched
        # and the start of UNIX time, as expressed as a float, will always do.
        last_sql_run = 0.0

        # We look up messages up to this point in time, which is equal to the start of our job.
        pub_time_max = max_last.as_float

        # We assume there is always one cluster in the database and we can skip its ID
        cluster_id = None

        # Always create a new session so as not to block the database
        '''
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_sql_msg_ids_by_sub_key(
                session, cluster_id, sub_key, last_sql_run, pub_time_max, include_unexpired_only=False, needs_result=True)

        # Convert SQL results to a dict that we can easily work with
        result = [elem._asdict() for elem in result]
        '''

        print(111, result)

        suffix = self._get_suffix(result)
        self.logger.info('CLEANSUB: Found %s message%sfor sub_key `%s` (ext: %s)', len(result), suffix, sub_key, sub['ext_client_id'])

        if result:
            table = tabulate_dictlist(result)
            self.logger.info('CLEANSUB: ** Messages to clean up for sub_key `%s` **\n%s', sub_key, table)
            self._cleanup_msg_group(sub_key, result)

# ################################################################################################################################

    def cleanup_pub_sub(self):

        # We will find all subscribers that did not interact with us for at least that many hours
        delta_not_interacted = Config.DeltaNotInteracted

        # Start of our cleanup procedure
        now = datetime.utcnow()

        # Turn hours into a UNIX time object, as expected by the database
        max_last_dt    = now - timedelta(hours=delta_not_interacted)
        max_last_float = datetime_to_ms(max_last_dt)

        max_last = MaxLast()
        max_last.as_float    = max_last_float
        max_last.as_datetime = max_last_dt

        # Find all subscribers in the database ..
        subs = self._get_subscriptions(max_last, delta_not_interacted)
        len_subs = len(subs)

        # .. and clean up them all, if needed.
        for sub in subs:
            self.logger.info('CLEANSUB: Cleaning up subscription %s/%s; %s -> %s',
                sub['idx'], len_subs, sub['sub_key'], sub['endpoint_name'])
            self._cleanup_sub(max_last, sub)

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
