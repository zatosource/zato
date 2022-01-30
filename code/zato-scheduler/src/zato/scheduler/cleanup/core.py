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
from zato.common.odb.query.cleanup import delete_queue_messages, get_subscriptions
from zato.common.odb.query.pubsub.delivery import get_sql_msg_ids_by_sub_key
from zato.common.util.api import grouper, set_up_logging, tabulate_dictlist
from zato.common.util.time_ import datetime_from_ms, datetime_to_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, dictlist, stranydict, strlist
    from zato.scheduler.server import Config
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

class MaxLast:
    as_float:    'float'
    as_datetime: 'datetime'

# ################################################################################################################################
# ################################################################################################################################

class CleanupConfig:
    DeltaNotInteracted = 86_400 # In seconds, 60 seconds * 60 minutes * 24 hours = 86_400 seconds
    MsgDeleteBatchSize = 50

# ################################################################################################################################
# ################################################################################################################################

class CleanupResult:
    sk_list:  'strlist'
    total_messages: int

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

        suffix = self._get_suffix(out)

        self.logger.info('CleanSub: Returning %s subscription%swith last interaction time older than %s (delta: %s seconds)',
            len(out), suffix, max_last.as_datetime, delta_not_interacted)

        if out:
            table = tabulate_dictlist(out)
            self.logger.info('CleanSub: ** Subscriptions to clean up **\n%s', table)

        return out

# ################################################################################################################################

    def _cleanup_msg_list(self, cleanup_result:'CleanupResult', sub_key:'str', msg_list:'dictlist') -> 'None':

        batch_size = CleanupConfig.MsgDeleteBatchSize

        groups = grouper(batch_size, msg_list)
        groups = list(groups)
        len_groups = len(groups)

        suffix = self._get_suffix(groups, needs_space=False)
        self.logger.info('CleanSub: Message(s) for `%s` turned into %s group%s, batch_size:%s',
            sub_key, len_groups, suffix, batch_size)

        # Note that messages for each subscriber are deleted under a new session
        with closing(self.config.odb.session()) as session: # type: ignore

            # Iterate over groups to delete each of them ..
            for idx, group in enumerate(groups, 1):

                # .. extract message IDs from each group ..
                msg_id_list = [elem['pub_msg_id'] for elem in group if elem]

                # .. log what we are about to do ..
                self.logger.info('CleanSub: Deleting group %s/%s (%s)', idx, len_groups, sub_key)

                # .. delete the group ..
                delete_queue_messages(session, msg_id_list)

                # .. make sure to commit the progress of the transaction ..
                session.commit()

                # .. store for later use ..
                cleanup_result.total_messages += len(msg_id_list)

                # .. and confirm that we did it.
                self.logger.info('CleanSub: Deleted  group %s/%s (%s)', idx, len_groups, sub_key)

# ################################################################################################################################

    def _cleanup_sub(self, cleanup_result:'CleanupResult', max_last:'MaxLast', sub:'stranydict') -> 'None':

        # Local aliases
        sub_key = sub['sub_key']

        self.logger.info('CleanSub: ---------------')
        self.logger.info('CleanSub: Looking up queue messages for %s', sub_key)

        # We look up all the messages in the database which is why the last_sql_run
        # needs to be set to a value that will be always matched
        # and the start of UNIX time, as expressed as a float, will always do.
        last_sql_run = 0.0

        # We look up messages up to this point in time, which is equal to the start of our job
        # (in seconds, hence the division, because we go from milliseconds up to seconds).
        pub_time_max = max_last.as_float / 1000

        # We assume there is always one cluster in the database and we can skip its ID
        cluster_id = None

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_sql_msg_ids_by_sub_key(
                session, cluster_id, sub_key, last_sql_run, pub_time_max, include_unexpired_only=False, needs_result=True)

        # Convert SQL results to a dict that we can easily work with
        result = [elem._asdict() for elem in result]

        suffix = self._get_suffix(result)
        self.logger.info('CleanSub: Found %s message%sfor sub_key `%s` (ext: %s)', len(result), suffix, sub_key, sub['ext_client_id'])

        if result:
            table = tabulate_dictlist(result)
            self.logger.debug('CleanSub: ** Messages to clean up for sub_key `%s` **\n%s', sub_key, table)
            self._cleanup_msg_list(cleanup_result, sub_key, result)

        # At this point, we have already deleted all the enqueued messages for all the subscribers
        # that we have not seen in DeltaNotInteracted hours. It means that we can proceed now
        # to delete each subscriber too because we know that it was not cascade to any of its
        # now-already-deleted messages. However, we do not do it using SQL queries
        # because there may still exist references to such subscribers among self.pubsub and tasks in servers.
        # Thus, we invoke our server, telling it that a given subscriber can be deleted, and the server
        # will know what to delete and clean up next. Again, note that at this point there are no outstanding
        # messages for that subscribers because we have just deleted them (or, possibly, a few more will have been enqueued
        # by the time the server receives our request) which means that the server's action will not cascade
        # to many rows in the queue table which in turn means that the database will not block for a long time.
        self.logger.info('CleanSub: Notifying server to delete sub_key `%s`', sub_key)

        # Now, we can append the sub_key to the list of what has been processed
        cleanup_result.sk_list.append(sub_key)

# ################################################################################################################################

    def cleanup_pub_sub(self) -> 'CleanupResult':

        # Response to produce
        cleanup_result = CleanupResult()
        cleanup_result.sk_list = []
        cleanup_result.total_messages = 0

        # We will find all subscribers that did not interact with us for at least that many seconds
        delta_not_interacted = int(os.environ.get('ZATO_SCHED_DELTA_NOT_INTERACT') or 0)
        delta_not_interacted = delta_not_interacted or CleanupConfig.DeltaNotInteracted

        # Start of our cleanup procedure
        now = datetime.utcnow()

        # Turn hours into a UNIX time object, as expected by the database
        max_last_dt    = now - timedelta(seconds=delta_not_interacted)
        max_last_float = datetime_to_ms(max_last_dt)

        max_last = MaxLast()
        max_last.as_float    = max_last_float
        max_last.as_datetime = max_last_dt

        # Find all subscribers in the database ..
        subs = self._get_subscriptions(max_last, delta_not_interacted)
        len_subs = len(subs)

        # .. and clean up them all, if needed.
        for sub in subs:
            sub_key = sub['sub_key']
            endpoint_name = sub['endpoint_name']
            self.logger.info('CleanSub: Cleaning up subscription %s/%s; %s -> %s', sub['idx'], len_subs, sub_key, endpoint_name)
            self._cleanup_sub(cleanup_result, max_last, sub)

        #
        # TODO: Add cleanup of queue messages that have no subscribers because
        # ..... sub_key in pubsub_endp_msg_queue does not point to pubsub_sub.
        #

        return cleanup_result

# ################################################################################################################################

    def run(self) -> 'CleanupResult':

        # Clean up old pub/sub objects
        cleanup_result = self.cleanup_pub_sub()

        self.logger.info('CleanSub: Processed %d message(s) from sk_list: %s',
            cleanup_result.total_messages, cleanup_result.sk_list)

        return cleanup_result

# ################################################################################################################################
# ################################################################################################################################

def run_cleanup():

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

    # Build and initialize object responsible for cleanup tasks ..
    cleanup_manager = CleanupManager(repo_location)
    cleanup_manager.init()

    # .. if we are here, it means that we can start our work.
    return cleanup_manager.run()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = run_cleanup()

# ################################################################################################################################
# ################################################################################################################################
