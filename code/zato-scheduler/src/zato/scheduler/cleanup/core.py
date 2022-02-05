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
from dataclasses import dataclass
from datetime import datetime, timedelta
from json import loads
from logging import captureWarnings, getLogger

# gevent
from gevent import sleep

# Zato
from zato.broker.client import BrokerClient
from zato.common.broker_message import SCHEDULER
from zato.common.odb.query.cleanup import delete_queue_messages, delete_topic_messages, get_messages, get_subscriptions
from zato.common.odb.query.pubsub.delivery import get_sql_msg_ids_by_sub_key
from zato.common.odb.query.pubsub.topic import get_topics_basic_data
from zato.common.typing_ import cast_, list_
from zato.common.util.api import grouper, set_up_logging, tabulate_dictlist
from zato.common.util.time_ import datetime_from_ms, datetime_to_ms
from zato.scheduler.util import set_up_zato_client

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

topic_ctx_list = list_['TopicCtx']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DeltaCtx:

    topic_min_retention:  'int'
    delta_not_interacted: 'int'

    not_iteracted_max_last_as_float:    'float'
    not_iteracted_max_last_as_datetime: 'datetime'

    topic_min_retention_as_float:    'float'
    topic_min_retention_as_datetime: 'datetime'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GroupsCtx:
    items: 'anylist'
    len_items: 'int'
    len_groups: 'int'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TopicCtx:
    id:   'int'
    name: 'str'
    messages: 'dictlist'
    groups_ctx: 'GroupsCtx'
    len_messages: 'int'
    min_retention_time: 'int'

# ################################################################################################################################
# ################################################################################################################################

class CleanupConfig:

    # One day in seconds; 60 seconds * 60 minutes * 24 hours = 86_400 seconds
    TopicRetentionTime = 86_400

    # (As above)
    DeltaNotInteracted = 86_400

    # How many messages to delete from a queue or topic in one batch
    MsgDeleteBatchSize = 50

    # How long to sleep after deleting messages from a single group (no matter if queue, topic or subscriber)
    DeleteSleepTime = 0.2 # In seconds

# ################################################################################################################################
# ################################################################################################################################

class CleanupResult:
    run_id: 'str'
    all_topics: 'int'
    pubsub_sk_list:  'strlist'
    pubsub_total_queue_messages: 'int'
    topics_cleaned_up: 'topic_ctx_list'

# ################################################################################################################################
# ################################################################################################################################

class CleanupManager:
    logger:        'Logger'
    config:        'Config'
    repo_location: 'str'
    broker_client: 'BrokerClient'

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

        # Configures a client to Zato servers
        self.zato_client = set_up_zato_client(self.config.main)
        self.broker_client = BrokerClient(zato_client=self.zato_client, server_rpc=None, scheduler_config=None)

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

    def _build_groups(self, task_id:'str', label:'str', msg_list:'dictlist', group_size:'int', ctx_id:'str') -> 'GroupsCtx':
        out = GroupsCtx()

        groups = grouper(group_size, msg_list)
        groups = list(groups)
        len_groups = len(groups)

        out.items = groups
        out.len_items = len_groups
        out.len_groups = len_groups

        suffix = self._get_suffix(groups, needs_space=False)
        self.logger.info('%s: %s %s turned into %s group%s, group_size:%s (%s)',
            task_id, len(msg_list), label, len_groups, suffix, group_size, ctx_id)

        return out

# ################################################################################################################################

    def _get_subscriptions(self, task_id:'str', delta_ctx:'DeltaCtx') -> 'anylist':

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_subscriptions(task_id, session, delta_ctx.not_iteracted_max_last_as_float)

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

        self.logger.info('%s: Returning %s subscription%swith last interaction time older than %s (delta: %s seconds)',
            task_id, len(out), suffix, delta_ctx.not_iteracted_max_last_as_datetime, delta_ctx.delta_not_interacted)

        if out:
            table = tabulate_dictlist(out)
            self.logger.info('%s: ** Subscriptions to clean up **\n%s', task_id, table)

        return out

# ################################################################################################################################

    def _cleanup_msg_list(self, task_id:'str', cleanup_result:'CleanupResult', sub_key:'str', msg_list:'dictlist') -> 'None':

        self.logger.info('%s: Building groups for sub_key -> %s', task_id, sub_key)
        groups_ctx = self._build_groups(task_id, 'queue message(s)', msg_list, CleanupConfig.MsgDeleteBatchSize, sub_key)

        # Note that messages for each subscriber are deleted under a new session
        with closing(self.config.odb.session()) as session: # type: ignore

            # Iterate over groups to delete each of them ..
            for idx, group in enumerate(groups_ctx.items, 1):

                # .. extract message IDs from each group ..
                msg_id_list = [elem['pub_msg_id'] for elem in group if elem]

                # .. log what we are about to do ..
                self.logger.info('%s: Deleting queue message group %s/%s (%s)', task_id, idx, groups_ctx.len_items, sub_key)

                # .. delete the group ..
                delete_queue_messages(session, msg_id_list)

                # .. make sure to commit the progress of the transaction ..
                session.commit()

                # .. store for later use ..
                cleanup_result.pubsub_total_queue_messages += len(msg_id_list)

                # .. confirm that we did it ..
                self.logger.info('%s: Deleted  group %s/%s (%s)', task_id, idx, groups_ctx.len_items, sub_key)

                # .. and sleep for a moment so as not to overwhelm the database.
                sleep(CleanupConfig.DeleteSleepTime)

# ################################################################################################################################

    def _cleanup_sub(self, task_id:'str', cleanup_result:'CleanupResult', delta_ctx:'DeltaCtx', sub:'stranydict') -> 'strlist':
        """ Cleans up an individual subscription. First it deletes old queue messages, then it notifies servers
        that a subscription object should be deleted as well.
        """

        # Local aliases
        sub_key = sub['sub_key']

        self.logger.info('%s: ---------------', task_id)
        self.logger.info('%s: Looking up queue messages for %s', task_id, sub_key)

        # We look up all the messages in the database which is why the last_sql_run
        # needs to be set to a value that will be always matched
        # and the start of UNIX time, as expressed as a float, will always do.
        last_sql_run = 0.0

        # We look up messages up to this point in time, which is equal to the start of our job
        # (in seconds, hence the division, because we go from milliseconds up to seconds).
        pub_time_max = delta_ctx.not_iteracted_max_last_as_float / 1000

        # We assume there is always one cluster in the database and we can skip its ID
        cluster_id = None

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            sk_queue_msg_list = get_sql_msg_ids_by_sub_key(
                session, cluster_id, sub_key, last_sql_run, pub_time_max, include_unexpired_only=False, needs_result=True)

        # Convert SQL results to a dict that we can easily work with
        sk_queue_msg_list = [elem._asdict() for elem in sk_queue_msg_list]

        suffix = self._get_suffix(sk_queue_msg_list)
        self.logger.info('%s: Found %s message%sfor sub_key `%s` (ext: %s)',
            task_id, len(sk_queue_msg_list), suffix, sub_key, sub['ext_client_id'])

        if sk_queue_msg_list:
            table = tabulate_dictlist(sk_queue_msg_list)
            self.logger.debug('%s: ** Messages to clean up for sub_key `%s` **\n%s', task_id, sub_key, table)
            self._cleanup_msg_list(task_id, cleanup_result, sub_key, sk_queue_msg_list)

        # At this point, we have already deleted all the enqueued messages for all the subscribers
        # that we have not seen in DeltaNotInteracted hours. It means that we can proceed now
        # to delete each subscriber too because we know that it will not cascade to any of its
        # now-already-deleted messages. However, we do not do it using SQL queries
        # because there may still exist references to such subscribers among self.pubsub and tasks in servers.
        # Thus, we invoke our server, telling it that a given subscriber can be deleted, and the server
        # will know what to delete and clean up next. Again, note that at this point there are no outstanding
        # messages for that subscribers because we have just deleted them (or, possibly, a few more will have been enqueued
        # by the time the server receives our request) which means that the server's action will not cascade
        # to many rows in the queue table which in turn means that the database will not block for a long time.
        self.logger.info('%s: Notifying server to delete sub_key `%s`', task_id, sub_key)

        self.broker_client.invoke_async({
            'service': 'zato.pubsub.endpoint.delete-endpoint-queue',
            'action': SCHEDULER.DELETE_PUBSUB_SUBSCRIBER.value,
            'payload': {
                'sub_key': sub_key,
            }
        }, from_scheduler=True)

        # Now, we can append the sub_key to the list of what has been processed
        cleanup_result.pubsub_sk_list.append(sub_key)

        # Finally, we can return all the IDs of messages enqueued for that sub_key
        return sk_queue_msg_list

# ################################################################################################################################

    def _cleanup_subscriptions(
        self,
        task_id:'str',
        cleanup_result:'CleanupResult',
        delta_ctx:'DeltaCtx'
        ) -> 'CleanupResult':
        """ Cleans up all subscriptions - all the old queue messages as well as their subscribers.
        """

        # This is a list of all the pub_msg_id objects that we are going to remove from subsciption queues.
        # It does not contain messages residing in topics that do not have any subscribers.
        # Currently, we populate this list but we do not use it for anything.
        queue_msg_list = []

        # Find all subscribers in the database ..
        subs = self._get_subscriptions(task_id, delta_ctx)
        len_subs = len(subs)

        # .. and clean up their queues, if any were found ..
        for sub in subs:
            sub_key = sub['sub_key']
            endpoint_name = sub['endpoint_name']
            self.logger.info('%s: Cleaning up subscription %s/%s; %s -> %s',
                task_id, sub['idx'], len_subs, sub_key, endpoint_name)

            # Clean up this sub_key and get the list of message IDs found for it ..
            sk_queue_msg_list = self._cleanup_sub(task_id, cleanup_result, delta_ctx, sub)

            # .. append the per-sub_key message to the overall list of messages found for subscribers.
            queue_msg_list.extend(sk_queue_msg_list)

        self.logger.info(f'{task_id}: Cleaned up %d pub/sub queue message(s) from sk_list: %s',
            cleanup_result.pubsub_total_queue_messages, cleanup_result.pubsub_sk_list)

        return cleanup_result

# ################################################################################################################################

    def _get_topics(self, task_id:'str', delta_ctx:'DeltaCtx') -> topic_ctx_list:

        # Our response to produce
        out = []

        # Topics found represented as dicts, not TopicCtx objects.
        # We use it for logging purposes because otherwise TopicCtx objects
        # would log their still empty information about messages, which could be misleading,
        # as though there were no messages for topics.
        topics_found = []

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_topics_basic_data(session)

        # Convert SQL results to a dict that we can easily work with
        result = [elem._asdict() for elem in result]

        # Extrat minimum retention time from each topic. If it is not found, use the default one.
        for topic_dict in result:

            # This is always a dict
            topic_dict = cast_('dict', topic_dict)

            # Remove all the opaque attributes because we need only the minimum retention time
            opaque = topic_dict.pop('opaque1')
            if opaque:
                opaque = loads(opaque)
            else:
                opaque = opaque or {}

            # Not all topics will have the minimum retention time configured,
            # in which case we use the relevant value from our configuration object.
            min_retention_time = opaque.get('min_retention_time') or delta_ctx.topic_min_retention
            topic_dict['min_retention_time'] = min_retention_time

            # Add the now ready topic dict to a list that the logger will use later
            topics_found.append(topic_dict)

            # Populate the result for our caller's benefit
            topic_ctx = TopicCtx()
            topic_ctx.id   = topic_dict['id']
            topic_ctx.name = topic_dict['name']
            topic_ctx.min_retention_time = topic_dict['min_retention_time']
            topic_ctx.messages = []
            topic_ctx.len_messages = 0

            out.append(topic_ctx)

        self.logger.info('%s: Topics found -> %s', task_id, topics_found)

        return out

# ################################################################################################################################

    def _delete_messages_from_topic_group(self, task_id:'str', topic_ctx:'TopicCtx') -> 'None':

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore

            for idx, group in enumerate(topic_ctx.groups_ctx.items, 1):

                # Local alias ..
                groups_ctx = topic_ctx.groups_ctx

                # .. log what we are about to do ..
                self.logger.info('%s: Deleting topic message group %s/%s (%s)',
                    task_id, idx, groups_ctx.len_groups, topic_ctx.name)

                # .. extract msg IDs from each dictionary in the group ..
                msg_id_list = [elem['pub_msg_id'] for elem in group if elem]

                # .. delete the group ..
                delete_topic_messages(session, msg_id_list)

                # .. make sure to commit the progress of the transaction ..
                session.commit()

                # .. sleep for a moment so as not to overwhelm the database ..
                sleep(CleanupConfig.DeleteSleepTime)

# ################################################################################################################################

    def _delete_messages_from_topics(
        self,
        task_id:'str',
        topics_to_clean_up: 'topic_ctx_list'
        ) -> 'None':

        # Iterate through each topic to clean it up
        for topic_ctx in topics_to_clean_up:

            # .. og what we are about to do ..
            self.logger.info('%s: Cleaning up %s message(s) from topic %s', task_id, topic_ctx.len_messages, topic_ctx.name)

            # .. assign to each topics individual groups of messages to be deleted ..
            topic_ctx.groups_ctx = self._build_groups(
                task_id, 'topic message(s)', topic_ctx.messages, CleanupConfig.MsgDeleteBatchSize, topic_ctx.name)

            # .. and clean it up now.
            self._delete_messages_from_topic_group(task_id, topic_ctx)

# ################################################################################################################################

    def _cleanup_messages_from_topics(
        self,
        task_id:'str',
        cleanup_result:'CleanupResult',
        delta_ctx:'DeltaCtx'
        ) -> 'None':

        # A dictionary mapping all the topics that have any messages to be deleted
        topics_to_clean_up = [] # type: topic_ctx_list

        # First, get all the topics that we can process
        topics = self._get_topics(task_id, delta_ctx)

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore

            for topic_ctx in topics:

                # Look up all the messages that can be deleted from that topic in the database
                messages_for_topic = get_messages(task_id, session, topic_ctx.id, topic_ctx.name)

                # .. convert the messages to dicts so as not to keep references to database objects ..
                messages_for_topic = [elem._asdict() for elem in messages_for_topic]

                # .. populate the context object with the newest information ..
                topic_ctx.messages.extend(messages_for_topic)
                topic_ctx.len_messages = len(messages_for_topic)

                self.logger.info('%s: Found %d message(s) for topic %s', task_id, topic_ctx.len_messages, topic_ctx.name)

                # Save for later use if there are any messages that can be deleted for that topic
                if topic_ctx.len_messages:
                    topics_to_clean_up.append(topic_ctx)

        # Remove messages from all the topics found ..
        self._delete_messages_from_topics(task_id, topics_to_clean_up)

        # .. and assign the context object for later use, e.g. in tests.
        cleanup_result.topics_cleaned_up = topics_to_clean_up

# ################################################################################################################################

    def cleanup_pub_sub(
        self,
        task_id:'str',
        cleanup_result:'CleanupResult',
        delta_ctx:'DeltaCtx'
        ) -> 'CleanupResult':

        # First, clean up all the old messages from subscription queues ..
        self._cleanup_subscriptions(task_id, cleanup_result, delta_ctx)

        # Now, we can proceed and delete the actual message objects because we know that their
        # queue references are already deleted.
        self._cleanup_messages_from_topics(task_id, cleanup_result, delta_ctx)

        return cleanup_result

# ################################################################################################################################

    def run(self) -> 'CleanupResult':

        # Local aliases
        now = datetime.utcnow()

        # This uniquely identifies our run
        run_id = f'{now.year}{now.month}{now.day}-{now.hour:02}{now.minute:02}{now.second:02}'

        # Response to produce
        cleanup_result = CleanupResult()
        cleanup_result.run_id = run_id
        cleanup_result.all_topics = 0
        cleanup_result.pubsub_sk_list = []
        cleanup_result.pubsub_total_queue_messages = 0

        # We will find all objects, such as subscribers or messages
        # that did not interact with us for at least that many seconds
        delta = int(os.environ.get('ZATO_SCHED_DELTA') or 0)

        topic_min_retention  = delta or CleanupConfig.TopicRetentionTime
        delta_not_interacted = delta or CleanupConfig.DeltaNotInteracted

        # Turn hours into a UNIX time object, as expected by the database

        not_iteracted_max_last_dt    = now - timedelta(seconds=delta_not_interacted)
        not_iteracted_max_last_float = datetime_to_ms(not_iteracted_max_last_dt)

        topic_min_retention_dt    = now - timedelta(seconds=topic_min_retention)
        topic_min_retention_float = datetime_to_ms(topic_min_retention_dt)

        # This is reusable across tasks
        delta_ctx = DeltaCtx()

        delta_ctx.topic_min_retention  = topic_min_retention
        delta_ctx.delta_not_interacted = delta_not_interacted

        delta_ctx.topic_min_retention_as_float    = topic_min_retention_float
        delta_ctx.topic_min_retention_as_datetime = topic_min_retention_dt

        delta_ctx.not_iteracted_max_last_as_float    = not_iteracted_max_last_float
        delta_ctx.not_iteracted_max_last_as_datetime = not_iteracted_max_last_dt

        self.logger.info('Starting cleanup tasks: %s; delta_ctx -> %s', run_id, delta_ctx)

        # IDs for our task
        task_id = f'CleanUp-{run_id}'

        # Clean up old pub/sub objects
        cleanup_result = self.cleanup_pub_sub(task_id, cleanup_result, delta_ctx)

        # TODO: Clean up queue messages that genuinely expired
        # TODO: Clean up topic messages that genuinely expired
        # TODO: Add maximum expiry time to topics and queues
        # TODO: Add max. number of subscribers per topic

        return cleanup_result

# ################################################################################################################################
# ################################################################################################################################

def run_cleanup() -> 'CleanupResult':

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

    # .. if we are here, it means that we can start our work ..
    result = cleanup_manager.run()
    return result

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = run_cleanup()

# ################################################################################################################################
# ################################################################################################################################
