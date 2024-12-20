# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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
from zato.common.api import PUBSUB
from zato.common.broker_message import SCHEDULER
from zato.common.marshal_.api import Model
from zato.common.odb.query.cleanup import delete_queue_messages, delete_topic_messages, \
    get_topic_messages_already_expired, get_topic_messages_with_max_retention_reached, \
    get_topic_messages_without_subscribers, get_subscriptions
from zato.common.odb.query.pubsub.delivery import get_sql_msg_ids_by_sub_key
from zato.common.odb.query.pubsub.topic import get_topics_basic_data
from zato.common.typing_ import cast_, list_
from zato.common.util.api import grouper, set_up_logging, tabulate_dictlist
from zato.common.util.time_ import datetime_from_ms, datetime_to_sec
from zato.scheduler.util import set_up_zato_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from logging import Logger
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, callable_, dictlist, dtnone, floatnone, stranydict, strlist, \
        strlistdict
    from zato.scheduler.server import Config
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_default_pubsub = PUBSUB.DEFAULT

topic_ctx_list = list_['TopicCtx']

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
    len_messages: 'int'
    limit_retention:      'int'
    limit_retention_dt: 'datetime'
    limit_retention_float: 'float'
    limit_message_expiry: 'int'
    limit_sub_inactivity: 'int'
    groups_ctx: 'GroupsCtx'

# ################################################################################################################################
# ################################################################################################################################

class CleanupConfig:

    # One day in seconds; 60 seconds * 60 minutes * 24 hours = 86_400 seconds
    TopicRetentionTime = 86_400

    # (As above)
    DeltaNotInteracted = 86_400

    # How many messages to delete from a queue or topic in one batch
    MsgDeleteBatchSize = 5000

    # How long to sleep after deleting messages from a single group (no matter if queue, topic or subscriber)
    DeleteSleepTime = 0.02 # In seconds

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CleanupCtx:
    run_id: 'str'
    found_all_topics: 'int'
    found_sk_list:  'strlist'
    found_total_queue_messages: 'int'
    found_total_expired_messages: 'int'

    now: 'float'
    now_dt: 'datetime'

    # This is a list of all topics in the system that will be processed. The list is built upfront, when the task starts.
    all_topics:        'topic_ctx_list'

    # All topics that will have been cleaned up, no matter why
    topics_cleaned_up: 'topic_ctx_list'

    # Topics cleaned up because they had no subscribers
    topics_without_subscribers: 'topic_ctx_list'

    # Topics cleaned up because their messages reached max. retention time allowed
    topics_with_max_retention_reached: 'topic_ctx_list'

    # Topics cleaned up because they contained messages that were expired
    topics_with_expired_messages: 'topic_ctx_list'

    # A lits of IDs of messages that were found to have expired
    expired_messages: 'dictlist'

    has_env_delta:               'bool'
    max_limit_sub_inactivity:    'int'
    max_limit_sub_inactivity_dt: 'datetime'

    max_last_interaction_time:    'float'
    max_last_interaction_time_dt: 'datetime'

    clean_up_subscriptions: 'bool'
    clean_up_topics_without_subscribers: 'bool'
    clean_up_topics_with_max_retention_reached: 'bool'
    clean_up_queues_with_expired_messages: 'bool'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CleanupPartsEnabled(Model):

    subscriptions: 'bool'
    topics_without_subscribers: 'bool'
    topics_with_max_retention_reached: 'bool'
    queues_with_expired_messages: 'bool'

# ################################################################################################################################
# ################################################################################################################################

class CleanupManager:
    logger:        'Logger'
    config:        'Config'
    repo_location: 'str'
    broker_client: 'BrokerClient'
    parts_enabled: 'CleanupPartsEnabled'

    def __init__(self, repo_location:'str', parts_enabled:'CleanupPartsEnabled') -> 'None':
        self.repo_location = repo_location
        self.parts_enabled = parts_enabled

# ################################################################################################################################

    def init(self):

        # Zato
        from zato.common.crypto.api import SchedulerCryptoManager
        from zato.scheduler.server import SchedulerServer, SchedulerServerConfig

        # Make sure we are in the same directory that the scheduler is in
        base_dir = os.path.join(self.repo_location, '..', '..')
        base_dir = os.path.abspath(base_dir)
        os.chdir(base_dir)

        # Build our main configuration object
        self.config = SchedulerServerConfig.from_repo_location(
            SchedulerServer.server_type,
            self.repo_location,
            SchedulerServer.conf_file_name,
            SchedulerCryptoManager
        )

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

    def _get_subscriptions(self, task_id:'str', topic_ctx:'TopicCtx', cleanup_ctx:'CleanupCtx') -> 'anylist':

        # Each topic has its own limit_sub_inactivity delta which means that we compute
        # the max_last_interaction time for each of them separately.
        # However, it is always possible to override the per-topic configuration
        # with an environment variable which is why we need to check that too.

        if cleanup_ctx.has_env_delta:
            topic_max_last_interaction_time_source = 'env'
            limit_sub_inactivity = cleanup_ctx.max_limit_sub_inactivity
            topic_max_last_interaction_time_dt = cleanup_ctx.max_last_interaction_time_dt
            topic_max_last_interaction_time = cleanup_ctx.max_last_interaction_time
        else:
            topic_max_last_interaction_time_source = 'topic'
            limit_sub_inactivity = topic_ctx.limit_sub_inactivity
            topic_max_last_interaction_time_dt = cleanup_ctx.now_dt - timedelta(seconds=limit_sub_inactivity)
            topic_max_last_interaction_time = datetime_to_sec(topic_max_last_interaction_time_dt)

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore
            result = get_subscriptions(task_id, session, topic_ctx.id, topic_ctx.name,
                topic_max_last_interaction_time, topic_max_last_interaction_time_dt, topic_max_last_interaction_time_source)

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

        msg = '%s: Returning %s subscription%sfor topic %s '
        msg += 'with no interaction or last interaction time older than `%s` (s:%s; delta: %s; topic-delta:%s)'

        self.logger.info(msg, task_id, len(out), suffix, topic_ctx.name, topic_max_last_interaction_time_dt,
            topic_max_last_interaction_time_source,
            limit_sub_inactivity,
            topic_ctx.limit_sub_inactivity,
        )

        if out:
            table = tabulate_dictlist(out, skip_keys='topic_opaque')
            self.logger.info('%s: ** Subscriptions to clean up **\n%s', task_id, table)

        return out

# ################################################################################################################################

    def _cleanup_queue_msg_list(
        self,
        task_id:'str',
        cleanup_ctx:'CleanupCtx',
        ctx_label:'str',
        ctx_id:'str',
        msg_list:'dictlist'
    ) -> 'None':

        self.logger.info('%s: Building queue message groups for %s -> %s', task_id, ctx_label, ctx_id)
        groups_ctx = self._build_groups(task_id, 'queue message(s)', msg_list, CleanupConfig.MsgDeleteBatchSize, ctx_id)

        # Note that messages for each subscriber are deleted under a new session
        with closing(self.config.odb.session()) as session: # type: ignore

            # Iterate over groups to delete each of them ..
            for idx, group in enumerate(groups_ctx.items, 1):

                # .. extract message IDs from each group ..
                msg_id_list = [elem['pub_msg_id'] for elem in group if elem]

                # .. log what we are about to do ..
                self.logger.info('%s: Deleting queue message group %s/%s (%s -> %s)',
                    task_id, idx, groups_ctx.len_items, ctx_label, ctx_id)

                # .. delete the group ..
                delete_queue_messages(session, msg_id_list)

                # .. make sure to commit the progress of the transaction ..
                session.commit()

                # .. store for later use ..
                cleanup_ctx.found_total_queue_messages += len(msg_id_list)

                # .. confirm that we did it ..
                self.logger.info('%s: Deleted group %s/%s (%s -> %s)',
                    task_id, idx, groups_ctx.len_items, ctx_label, ctx_id)

                # .. and sleep for a moment so as not to overwhelm the database.
                sleep(CleanupConfig.DeleteSleepTime)

# ################################################################################################################################

    def _cleanup_sub(self, task_id:'str', cleanup_ctx:'CleanupCtx', sub:'stranydict') -> 'strlist':
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
        pub_time_max = cleanup_ctx.now

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
            self._cleanup_queue_msg_list(task_id, cleanup_ctx, 'sub-cleanup', sub_key, sk_queue_msg_list)

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
        cleanup_ctx.found_sk_list.append(sub_key)

        # Finally, we can return all the IDs of messages enqueued for that sub_key
        return sk_queue_msg_list

# ################################################################################################################################

    def _cleanup_subscriptions(
        self,
        task_id:'str',
        cleanup_ctx:'CleanupCtx'
        ) -> 'CleanupCtx':
        """ Cleans up all subscriptions - all the old queue messages as well as their subscribers.
        """

        # For each topic we already know it exists ..
        for topic_ctx in cleanup_ctx.all_topics:

            # This is a list of all the pub_msg_id objects that we are going to remove from subsciption queues.
            # It does not contain messages residing in topics that do not have any subscribers.
            # Currently, we populate this list but we do not use it for anything.
            queue_msg_list = []

            # Find all subscribers in the database ..
            subs = self._get_subscriptions(task_id, topic_ctx, cleanup_ctx)
            len_subs = len(subs)

            # .. and clean up their queues, if any were found ..
            for sub in subs:
                sub_key = sub['sub_key']
                endpoint_name = sub['endpoint_name']
                self.logger.info('%s: Cleaning up subscription %s/%s; %s -> %s (%s)',
                    task_id, sub['idx'], len_subs, sub_key, endpoint_name, topic_ctx.name)

                # Clean up this sub_key and get the list of message IDs found for it ..
                sk_queue_msg_list = self._cleanup_sub(task_id, cleanup_ctx, sub)

                # .. append the per-sub_key message to the overall list of messages found for subscribers.
                queue_msg_list.extend(sk_queue_msg_list)

            self.logger.info(f'{task_id}: Cleaned up %d pub/sub queue message(s) from sk_list: %s (%s)',
                cleanup_ctx.found_total_queue_messages, cleanup_ctx.found_sk_list, topic_ctx.name)

            # .. and sleep for a moment so as not to overwhelm the database.
            sleep(CleanupConfig.DeleteSleepTime)

        return cleanup_ctx

# ################################################################################################################################

    def _get_topics(self, task_id:'str', cleanup_ctx:'CleanupCtx') -> topic_ctx_list:

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

            # Not all topics will have the minimum retention time and related data configured,
            # in which case we use the relevant value from our configuration object.
            # Observe that these are limits, expressed as integers, not timestamps based on these limits.
            limit_retention      = opaque.get('limit_retention')      or _default_pubsub.LimitTopicRetention
            limit_message_expiry = opaque.get('limit_message_expiry') or _default_pubsub.LimitMessageExpiry
            limit_sub_inactivity = opaque.get('limit_sub_inactivity') or _default_pubsub.LimitSubInactivity

            # Timestamps are computed here
            limit_retention_dt    = cleanup_ctx.now_dt - timedelta(seconds=limit_retention)
            limit_retention_float = datetime_to_sec(limit_retention_dt)

            # Add the now ready topic dict to a list that the logger will use later
            topics_found.append(topic_dict)

            # Populate the result for our caller's benefit
            topic_ctx = TopicCtx()
            topic_ctx.id   = topic_dict['id']
            topic_ctx.name = topic_dict['name']
            topic_ctx.limit_retention = limit_retention
            topic_ctx.limit_retention_dt = limit_retention_dt
            topic_ctx.limit_retention_float = limit_retention_float
            topic_ctx.limit_message_expiry = limit_message_expiry
            topic_ctx.limit_sub_inactivity = limit_sub_inactivity
            topic_ctx.messages = []
            topic_ctx.len_messages = 0

            out.append(topic_ctx)

        self.logger.info('%s: Topics found -> %s', task_id, topics_found)

        return out

# ################################################################################################################################

    def _delete_topic_messages_from_group(self, task_id:'str', groups_ctx:'GroupsCtx', topic_name:'str') -> 'None':

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore

            for idx, group in enumerate(groups_ctx.items, 1):

                # .. log what we are about to do ..
                self.logger.info('%s: Deleting topic message group %s/%s (%s)',
                    task_id, idx, groups_ctx.len_groups, topic_name)

                # .. extract msg IDs from each dictionary in the group ..
                msg_id_list = [elem['pub_msg_id'] for elem in group if elem]

                # .. delete the group ..
                delete_topic_messages(session, msg_id_list)

                # .. make sure to commit the progress of the transaction ..
                session.commit()

                # .. sleep for a moment so as not to overwhelm the database ..
                sleep(CleanupConfig.DeleteSleepTime)

# ################################################################################################################################

    def _delete_topic_messages(
        self,
        task_id:'str',
        topics_to_clean_up: 'topic_ctx_list',
        messages_to_delete: 'strlistdict',
        message_type_label: 'str',
        ) -> 'None':

        # Iterate through each topic to clean it up
        for topic_ctx in topics_to_clean_up:

            per_topic_messages_to_delete = messages_to_delete[topic_ctx.name]

            # .. log what we are about to do ..
            self.logger.info('%s: Cleaning up %s message(s) %s -> %s',
                task_id, len(per_topic_messages_to_delete), message_type_label, topic_ctx.name)

            # .. assign to each topics individual groups of messages to be deleted ..
            groups_ctx = self._build_groups(
                task_id, 'message(s)', per_topic_messages_to_delete, CleanupConfig.MsgDeleteBatchSize, topic_ctx.name)

            # .. and clean it up now.
            self._delete_topic_messages_from_group(task_id, groups_ctx, topic_ctx.name)

# ################################################################################################################################

    def _cleanup_topic_messages(
        self,
        task_id:'str',
        cleanup_ctx:'CleanupCtx',
        query:'callable_',
        message_type_label:'str',
        *,
        use_as_dict:'bool',
        use_topic_retention_time:'bool',
        max_time_dt: 'dtnone' = None,
        max_time_float: 'floatnone' = None,
        ) -> 'topic_ctx_list':

        # A dictionary mapping all the topics that have any messages to be deleted
        topics_to_clean_up = [] # type: topic_ctx_list

        # A dictionary mapping topic names to messages that need to be deleted from them
        messages_to_delete = {} # type: strlistdict

        # Always create a new session so as not to block the database
        with closing(self.config.odb.session()) as session: # type: ignore

            for topic_ctx in cleanup_ctx.all_topics:

                # We enter here if we check the max. allowed publication time
                # for each topic separately, based on its max. allowed retention time.
                # In other words, we are interested in topics that contain messages
                # whose retention time has been reached ..
                if use_topic_retention_time:
                    per_topic_max_time_dt = topic_ctx.limit_retention_dt
                    per_topic_max_time_float = topic_ctx.limit_retention_float

                # .. we enter here if simply want to find messages published
                # at any point in the past as long as it was before our task started.
                else:
                    per_topic_max_time_dt = max_time_dt
                    per_topic_max_time_float = max_time_float

                # Run our input query to look up messages to delete
                messages_for_topic = query(
                    task_id,
                    session,
                    topic_ctx.id,
                    topic_ctx.name,
                    per_topic_max_time_dt,
                    per_topic_max_time_float,
                )

                # .. convert the messages to dicts so as not to keep references to database objects ..
                # .. What method to choose depends on whether the underlying query uses SQLAlchemy ORM (with _asdict)
                # .. or whether it is a regular select statement, in which case dict() is used over a series of tuples.
                if use_as_dict:
                    messages_for_topic = [elem._asdict() for elem in messages_for_topic]
                else:
                    messages_for_topic = [dict(elem) for elem in messages_for_topic]

                # .. populate the context object with the newest information ..
                topic_ctx.len_messages = len(messages_for_topic)

                # .. populate the map of messages that need to be deleted
                per_topic_messages_to_delete_list = messages_to_delete.setdefault(topic_ctx.name, [])
                per_topic_messages_to_delete_list.extend(messages_for_topic)

                self.logger.info('%s: Found %d message(s) %s for topic %s',
                    task_id, topic_ctx.len_messages, message_type_label, topic_ctx.name)

                # Save for later use if there are any messages that can be deleted for that topic
                if topic_ctx.len_messages:
                    topic_ctx.messages.extend(per_topic_messages_to_delete_list)
                    topics_to_clean_up.append(topic_ctx)

                # .. sleep for a moment so as not to overwhelm the database ..
                sleep(CleanupConfig.DeleteSleepTime)

        # Remove messages from all the topics found ..
        self._delete_topic_messages(task_id, topics_to_clean_up, messages_to_delete, message_type_label)

        # .. and return all the processed topics to our caller.
        return topics_to_clean_up

# ################################################################################################################################

    def _cleanup_topic_messages_without_subscribers(
        self,
        task_id:'str',
        cleanup_ctx:'CleanupCtx'
        ) -> 'topic_ctx_list':

        #
        # This query will look up all the messages that can be deleted from a topic in the database based on two conditions.
        #
        # 1) A message must not have any subscribers
        # 2) A message must have been published before our task started
        #
        # Thanks to the second condition we do not delete messages that have been
        # published after our task started. Such messages may be included in a future run
        # in case they never see any subscribers, or perhaps their max. retention time will be reached,
        # but we are not concerned with them in the current run and the current query here.
        #
        # Note that this is akin to self._clean_up_queues_with_expired_messages but that other method's query
        # explicitly checks messages that do have subscribers with messages that expired
        # whereas here we do not check if the messages expired, we only check if there are no subscribers.
        #
        query = get_topic_messages_without_subscribers
        message_type_label = 'without subscribers'
        max_time_dt = cleanup_ctx.now_dt
        max_time_float = cleanup_ctx.now

        return self._cleanup_topic_messages(task_id, cleanup_ctx, query, message_type_label,
            use_as_dict=True,
            use_topic_retention_time=False, max_time_dt=max_time_dt, max_time_float=max_time_float)

# ################################################################################################################################

    def _cleanup_topic_messages_with_max_retention_reached(
        self,
        task_id:'str',
        cleanup_ctx:'CleanupCtx'
        ) -> 'topic_ctx_list':

        #
        # This query will look up all the messages that are still in topics
        # but their max. retention time has been reached.
        #
        query = get_topic_messages_with_max_retention_reached
        message_type_label = 'with max. retention reached'

        # These are explictly set to None because the max. publication time will be computed
        # for each topic separately in the cleanup function that we are calling below,
        # based on each of the topic's max retention time allowed.
        max_time_dt = None
        max_time_float = None

        return self._cleanup_topic_messages(task_id, cleanup_ctx, query, message_type_label,
            use_as_dict=True,
            use_topic_retention_time=True, max_time_dt=max_time_dt, max_time_float=max_time_float)

# ################################################################################################################################

    def _clean_up_queues_with_expired_messages(
        self,
        task_id:'str',
        cleanup_ctx:'CleanupCtx'
        ) -> 'topic_ctx_list':

        #
        # This query will look up all the messages that can be deleted from a topic in the database based on two conditions.
        #
        # 1) A message must not have any subscribers
        # 2) A message must have been published before our task started
        #
        # Thanks to the second condition we do not delete messages that have been
        # published after our task started. Such messages may be included in a future run
        # in case they never see any subscribers, or perhaps their max. retention time will be reached,
        # but we are not concerned with them in the current run and the current query here.
        #
        # Note that this is akin to self._cleanup_topic_messages_without_subscribers but that other method's query
        # explicitly looks up messages that have no subscribers - no matter if they are expired or not.
        #
        query = get_topic_messages_already_expired
        message_type_label = 'already expired'
        max_time_dt = cleanup_ctx.now_dt
        max_time_float = cleanup_ctx.now

        return self._cleanup_topic_messages(task_id, cleanup_ctx, query, message_type_label,
            use_as_dict=False,
            use_topic_retention_time=False, max_time_dt=max_time_dt, max_time_float=max_time_float)

# ################################################################################################################################

    def cleanup_pub_sub(
        self,
        task_id:'str',
        cleanup_ctx:'CleanupCtx'
        ) -> 'CleanupCtx':

        # First, clean up all the old messages from subscription queues
        # as well as subscribers that have not used the system in the last delta seconds.
        if cleanup_ctx.clean_up_subscriptions:
            self.logger.info('Entering _cleanup_subscriptions')
            self._cleanup_subscriptions(task_id, cleanup_ctx)

        # Clean up topics that contain messages without subscribers
        if cleanup_ctx.clean_up_topics_without_subscribers:
            self.logger.info('Entering _cleanup_topic_messages_without_subscribers')
            topics_cleaned_up = self._cleanup_topic_messages_without_subscribers(task_id, cleanup_ctx)
            cleanup_ctx.topics_cleaned_up.extend(topics_cleaned_up)
            cleanup_ctx.topics_without_subscribers.extend(topics_cleaned_up)

        # Clean up topics that contain messages whose max. retention time has been reached
        if cleanup_ctx.clean_up_topics_with_max_retention_reached:
            self.logger.info('Entering _cleanup_topic_messages_with_max_retention_reached')
            topics_cleaned_up = self._cleanup_topic_messages_with_max_retention_reached(task_id, cleanup_ctx)
            cleanup_ctx.topics_cleaned_up.extend(topics_cleaned_up)
            cleanup_ctx.topics_with_max_retention_reached.extend(topics_cleaned_up)

        # Clean up queues that contain messages which were already expired
        if cleanup_ctx.clean_up_queues_with_expired_messages:
            self.logger.info('Entering _clean_up_queues_with_expired_messages')
            topics_cleaned_up = self._clean_up_queues_with_expired_messages(task_id, cleanup_ctx)
            cleanup_ctx.topics_cleaned_up.extend(topics_cleaned_up)
            cleanup_ctx.topics_with_expired_messages.extend(topics_cleaned_up)
            for topic_ctx in topics_cleaned_up:
                cleanup_ctx.expired_messages.extend(topic_ctx.messages)
                cleanup_ctx.found_total_expired_messages += len(topic_ctx.messages)

        return cleanup_ctx

# ################################################################################################################################

    def run(self) -> 'CleanupCtx':

        # Local aliases
        now_dt = datetime.utcnow()

        # This uniquely identifies our run
        run_id = f'{now_dt.year}{now_dt.month}{now_dt.day}-{now_dt.hour:02}{now_dt.minute:02}{now_dt.second:02}'

        # IDs for our task
        task_id = f'CleanUp-{run_id}'

        # Log what parts of the cleanup procedure are enabled
        parts_enabled_log_msg = tabulate_dictlist([self.parts_enabled.to_dict()])
        self.logger.info('%s: Parts enabled: \n%s', task_id, parts_enabled_log_msg)

        # Overall context of the procedure, including a response to produce
        cleanup_ctx = CleanupCtx()
        cleanup_ctx.run_id = run_id
        cleanup_ctx.found_all_topics = 0
        cleanup_ctx.found_sk_list = []
        cleanup_ctx.found_total_queue_messages = 0
        cleanup_ctx.found_total_expired_messages = 0
        cleanup_ctx.topics_cleaned_up = []
        cleanup_ctx.topics_without_subscribers = []
        cleanup_ctx.topics_with_max_retention_reached = []
        cleanup_ctx.topics_with_expired_messages = []
        cleanup_ctx.expired_messages = []

        # What cleanup parts to run
        cleanup_ctx.clean_up_subscriptions = self.parts_enabled.subscriptions
        cleanup_ctx.clean_up_topics_without_subscribers = self.parts_enabled.topics_without_subscribers
        cleanup_ctx.clean_up_topics_with_max_retention_reached = self.parts_enabled.topics_with_max_retention_reached
        cleanup_ctx.clean_up_queues_with_expired_messages = self.parts_enabled.queues_with_expired_messages

        cleanup_ctx.now_dt = now_dt
        cleanup_ctx.now = datetime_to_sec(cleanup_ctx.now_dt)

        # Assign a list of topics found in the database
        cleanup_ctx.all_topics = self._get_topics(task_id, cleanup_ctx)

        # Note that this limit is in seconds ..
        cleanup_ctx.max_limit_sub_inactivity = max(item.limit_sub_inactivity for item in cleanup_ctx.all_topics)

        # Max. inactivity allowed can be always overridden through this environment variable
        env_max_limit_sub_inactivity = int(os.environ.get('ZATO_SCHED_DELTA') or 0)

        if env_max_limit_sub_inactivity:

            cleanup_ctx.has_env_delta = True
            cleanup_ctx.max_limit_sub_inactivity = env_max_limit_sub_inactivity

            max_last_interaction_time_dt = cleanup_ctx.now_dt - timedelta(seconds=env_max_limit_sub_inactivity)
            max_last_interaction_time    = datetime_to_sec(max_last_interaction_time_dt)

            cleanup_ctx.max_last_interaction_time = max_last_interaction_time
            cleanup_ctx.max_last_interaction_time_dt = max_last_interaction_time_dt

        else:
            cleanup_ctx.has_env_delta = False

        self.logger.info('Starting cleanup tasks: %s', task_id)

        # Clean up old pub/sub objects
        cleanup_ctx = self.cleanup_pub_sub(task_id, cleanup_ctx)

        return cleanup_ctx

# ################################################################################################################################
# ################################################################################################################################

def run_cleanup(
    clean_up_subscriptions: 'bool',
    clean_up_topics_without_subscribers: 'bool',
    clean_up_topics_with_max_retention_reached: 'bool',
    clean_up_queues_with_expired_messages: 'bool',
    scheduler_path:'str',
) -> 'CleanupCtx':

    # Always work with absolute paths
    scheduler_path = os.path.abspath(scheduler_path)

    # Make sure that the path exists
    if not os.path.exists(scheduler_path):
        raise Exception(f'Scheduler path not found: `{scheduler_path}')

    repo_location = os.path.join(scheduler_path, 'config', 'repo')
    repo_location = os.path.expanduser(repo_location)

    # Information about what cleanup parts / tasks are enabled
    parts_enabled = CleanupPartsEnabled()
    parts_enabled.subscriptions = clean_up_subscriptions
    parts_enabled.topics_without_subscribers = clean_up_topics_without_subscribers
    parts_enabled.topics_with_max_retention_reached = clean_up_topics_with_max_retention_reached
    parts_enabled.queues_with_expired_messages = clean_up_queues_with_expired_messages

    # Build and initialize object responsible for cleanup tasks ..
    cleanup_manager = CleanupManager(repo_location, parts_enabled)
    cleanup_manager.init()

    # .. if we are here, it means that we can start our work ..
    result = cleanup_manager.run()
    return result

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    scheduler_path = os.environ['ZATO_SCHEDULER_BASE_DIR']

    _ = run_cleanup(
        clean_up_subscriptions = True,
        clean_up_topics_without_subscribers = True,
        clean_up_topics_with_max_retention_reached = True,
        clean_up_queues_with_expired_messages = True,
        scheduler_path=scheduler_path
    )

# ################################################################################################################################
# ################################################################################################################################
