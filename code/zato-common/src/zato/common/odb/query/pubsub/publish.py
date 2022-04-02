# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from logging import DEBUG, getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage, PubSubTopic
from zato.common.pubsub import ensure_subs_exist, msg_pub_ignore
from zato.common.util.sql.retry import sql_op_with_deadlock_retry

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SQLSession
    from zato.common.typing_ import any_, callable_, strdictlist
    from zato.server.pubsub.model import sublist

# ################################################################################################################################
# ################################################################################################################################

logger_zato = getLogger('zato')
logger_pubsub = getLogger('zato_pubsub')

has_debug = True # logger_zato.isEnabledFor(DEBUG) or logger_pubsub.isEnabledFor(DEBUG)
DEBUG

# ################################################################################################################################
# ################################################################################################################################

MsgInsert = PubSubMessage.__table__.insert
EndpointTopicInsert = PubSubEndpointTopic.__table__.insert
EnqueuedMsgInsert = PubSubEndpointEnqueuedMessage.__table__.insert

MsgTable = PubSubMessage.__table__
TopicTable = PubSubTopic.__table__
EndpointTable = PubSubEndpoint.__table__
EndpointTopicTable = PubSubEndpointTopic.__table__

# ################################################################################################################################
# ################################################################################################################################

_float_str = PUBSUB.FLOAT_STRING_CONVERT
sub_only_keys = ('sub_pattern_matched', 'topic_name')

# ################################################################################################################################
# ################################################################################################################################

class PublishOpCtx:
    needs_topic_messages:'bool' = True
    needs_queue_messages:'bool' = True
    is_queue_insert_ok:'bool | str'   = 'not-set-yet'

    def __init__(self, pub_counter:'int') -> 'None':

        # This is a server-wide counter of messages published
        self.pub_counter = pub_counter

        # This is a counter increaed after each unsuccessful queue insertion attempt.
        self.queue_insert_attempt = 0

    def on_new_iter(self) -> 'None':

        # This is invoked in each iteration of a publication loop.

        # First, increase the publication attempt counter ..
        self.queue_insert_attempt += 1

        # .. now, reset out the indicator pointing to whether the insertion was successful.
        self.is_queue_insert_ok = 'not-set-yet'

    def get_counter_ctx_str(self) -> 'str':
        return f'{self.pub_counter}:{self.queue_insert_attempt}'

# ################################################################################################################################
# ################################################################################################################################

class PublishWithRetryManager:

    def __init__(
        self,

        now,         # type: float
        cid,         # type: str
        topic_id,    # type: int
        topic_name,  # type: str
        cluster_id,  # type: int
        pub_counter, # type: int

        session,          # type: SQLSession
        new_session_func, # type: callable_

        gd_msg_list,            # type: strdictlist
        subscriptions_by_topic, # type: sublist

    ) -> 'None':

        self.now = now
        self.cid = cid
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.cluster_id = cluster_id
        self.pub_counter = pub_counter

        self.session = session
        self.new_session_func = new_session_func

        self.gd_msg_list = gd_msg_list
        self.subscriptions_by_topic = subscriptions_by_topic

# ################################################################################################################################

    def run(self):

        # This is a reusable context object that will be employed
        # by all the iterations of the publication loop.
        publish_op_ctx = PublishOpCtx(self.pub_counter)

        # We make a reference to the subscriptions here because we may want to modify it
        # in case queue messages could not be inserted.
        subscriptions_by_topic = self.subscriptions_by_topic

        while publish_op_ctx.needs_queue_messages:

            # We have just entered a new iteration of this loop (possibly it is the first time)
            # so we need to carry out a few metadata-related tasks first.
            publish_op_ctx.on_new_iter()

            # This is reusable
            counter_ctx_str = publish_op_ctx.get_counter_ctx_str()

            if has_debug:
                logger_zato.info('sql_publish_with_retry -> %s -> is_ok.1:`%s`',
                    counter_ctx_str,
                    publish_op_ctx.is_queue_insert_ok
                )

            publish_op_ctx = _sql_publish_with_retry(
                publish_op_ctx,
                self.session,
                self.cid,
                self.cluster_id,
                self.topic_id,
                subscriptions_by_topic,
                self.gd_msg_list,
                self.now
            )

            if not publish_op_ctx.is_queue_insert_ok:

                if has_debug:
                    logger_zato.info('sql_publish_with_retry -> %s -> is_ok.2:`%s`',
                        counter_ctx_str,
                        publish_op_ctx.is_queue_insert_ok
                    )
                    has_debug

                # We may possibly need to filter out subscriptions that do not exist anymore - this is needed because
                # we took our list of subscribers from self.pubsub but it is possible that between the time
                # we got this list and when this transaction started, some of the subscribers
                # have been already deleted from the database so, if we were not filter them out, we would be
                # potentially trying to insert rows pointing to foreign keys that no longer exist.
                with closing(self.new_session_func()) as new_session: # type: ignore
                    subscriptions_by_topic = ensure_subs_exist(
                        new_session,
                        self.topic_name,
                        self.gd_msg_list,
                        subscriptions_by_topic,
                        '_sql_publish_with_retry',
                        counter_ctx_str
                    )

            else:
                has_debug

# ################################################################################################################################
# ################################################################################################################################

def _sql_publish_with_retry(
    publish_op_ctx:'PublishOpCtx',
    session,    # type: SQLSession
    cid,        # type: str
    cluster_id, # type: int
    topic_id,   # type: int
    subscriptions_by_topic, # type: sublist
    gd_msg_list, # type: strdictlist
    now          # type: float
) -> 'PublishOpCtx':
    """ A low-level implementation of sql_publish_with_retry.
    """

    # Added for type hints
    sub_keys_by_topic = 'default-sub-keys-by-topic'
    topic_messages_inserted = 'default-topic-messages-inserted'

    #
    # We need to temporarily remove selected keys from gd_msg_list while we insert the topic
    # messages only to bring back these keys later on when inserting the same messages for subscribers.
    #
    # The reason is that we want to avoid the "sqlalchemy.exc.CompileError: Unconsumed column names"
    # condition which is met when insert_topic_messages attempts to use columns that are needed
    # only by insert_queue_messages.
    #
    # An alternative to removing them temporarily would be to have two copies of the messages
    # but that could be expensive as they would be otherwise 99% the same, differing only
    # by these few, specific short keys.
    #

    # These message attributes are needed only by queue subscribers
    sub_only = {}

    # Go through each message and remove the keys that topics do not use
    for msg in gd_msg_list: # type: dict

        pub_msg_id = msg['pub_msg_id']
        sub_attrs = sub_only.setdefault(pub_msg_id, {})

        for name in sub_only_keys:
            sub_attrs[name] = msg.pop(name, None)

    # Publish messages - INSERT rows, each representing an individual message
    if publish_op_ctx.needs_topic_messages:
        topic_messages_inserted = insert_topic_messages(session, cid, gd_msg_list)
        publish_op_ctx.needs_topic_messages = False

    if has_debug:
        sub_keys_by_topic = sorted(elem.sub_key for elem in subscriptions_by_topic)
        logger_zato.info(
            'With topic_messages_inserted -> %s -> `%s` `%s` `%s` `%s` `%s` `%s` `%s`',
                publish_op_ctx.get_counter_ctx_str(),
                cid,
                topic_messages_inserted,
                cluster_id,
                topic_id,
                sub_keys_by_topic,
                gd_msg_list,
                now
            )

    # If any messages were inserted ..
    if publish_op_ctx.needs_queue_messages:

        # .. move references to the messages to each subscriber's queue ..
        if subscriptions_by_topic:

            try:

                # .. now, go through each message and add back the keys that topics did not use
                # .. but queues are going to need.
                for msg in gd_msg_list: # type: dict
                    pub_msg_id = msg['pub_msg_id']
                    for name in sub_only_keys:
                        msg[name] = sub_only[pub_msg_id][name]

                if has_debug:
                    logger_zato.info('Inserting queue messages for sub_keys_by_topic -> %s -> `%s`',
                        publish_op_ctx.get_counter_ctx_str(),
                        sub_keys_by_topic
                    )

                # This is the call that adds references to each of GD message for each of the input subscribers.
                insert_queue_messages(
                    session,
                    cluster_id,
                    subscriptions_by_topic,
                    gd_msg_list,
                    topic_id,
                    now,
                    cid
                )

                if has_debug:
                    logger_zato.info('Inserted queue messages -> %s -> `%s` `%s` `%s` `%s` `%s` `%s`',
                        publish_op_ctx.get_counter_ctx_str(),
                        cid, cluster_id, sub_keys_by_topic, gd_msg_list, topic_id, now)

                # No integrity error / no deadlock = all good
                is_queue_insert_ok = True

            except IntegrityError as e:
                logger_zato.info('Caught IntegrityError (_sql_publish_with_retry) -> %s -> `%s` `%s`',
                publish_op_ctx.get_counter_ctx_str(),
                e,
                cid)

                # If we have an integrity error here it means that our transaction, the whole of it,
                # was rolled back - this will happen on MySQL in case in case of deadlocks which may
                # occur because delivery tasks update the table that insert_queue_messages wants to insert to.
                # We need to return False for our caller to understand that the whole transaction needs
                # to be repeated.
                is_queue_insert_ok = False

            # Update publication context based on whether queue messages were inserted or not.
            publish_op_ctx.is_queue_insert_ok = is_queue_insert_ok
            publish_op_ctx.needs_queue_messages = not is_queue_insert_ok

        else:

            if has_debug:
                logger_zato.info('No subscribers in -> %s -> `%s`',
                publish_op_ctx.get_counter_ctx_str(),
                cid)

    return publish_op_ctx

# ################################################################################################################################

def sql_publish_with_retry(

    now,         # type: float
    cid,         # type: str
    topic_id,    # type: int
    topic_name,  # type: str
    cluster_id,  # type: int
    pub_counter, # type: int

    session,          # type: SQLSession
    new_session_func, # type: callable_

    gd_msg_list,            # type: strdictlist
    subscriptions_by_topic, # type: sublist
) -> 'PublishWithRetryManager':

    """ Populates SQL structures with new messages for topics and their counterparts in subscriber queues.
    In case of a deadlock will retry the whole transaction, per MySQL's requirements, which rolls back
    the whole of it rather than a deadlocking statement only.
    """

    # Build the manager object responsible for the publication ..
    publish_with_retry_manager = PublishWithRetryManager(
        now,
        cid,
        topic_id,
        topic_name,
        cluster_id,
        pub_counter,

        session,
        new_session_func,

        gd_msg_list,
        subscriptions_by_topic,
    )

    # .. publish the message(s) ..
    publish_with_retry_manager.run()

    # .. and return the manager to our caller.
    return publish_with_retry_manager

# ################################################################################################################################

def _insert_topic_messages(session:'SQLSession', msg_list:'strdictlist') -> 'None':
    """ A low-level implementation for insert_topic_messages.
    """
    # Delete keys that cannot be inserted in SQL
    for msg in msg_list: # type: dict
        for name in msg_pub_ignore:
            msg.pop(name, None)

    session.execute(MsgInsert().values(msg_list))

# ################################################################################################################################

def insert_topic_messages(session:'SQLSession', cid:'str', msg_list:'strdictlist') -> 'any_':
    """ Publishes messages to a topic, i.e. runs an INSERT that inserts rows, one for each message.
    """
    try:
        return sql_op_with_deadlock_retry(cid, 'insert_topic_messages', _insert_topic_messages, session, msg_list)

    # Catch duplicate MsgId values sent by clients
    except IntegrityError:

        if has_debug:
            logger_zato.info('Caught IntegrityError (insert_topic_messages) `%s` `%s`', cid, format_exc())
        raise

# ################################################################################################################################

def _insert_queue_messages(session:'SQLSession', queue_msgs:'strdictlist') -> 'None':
    """ A low-level call to enqueue messages.
    """
    session.execute(EnqueuedMsgInsert().values(queue_msgs))

# ################################################################################################################################

def insert_queue_messages(
    session,    # type: SQLSession
    cluster_id, # type: int
    subscriptions_by_topic, # type: sublist
    msg_list, # type: strdictlist
    topic_id, # type: int
    now,      # type: float
    cid       # type: str
)-> 'any_':
    """ Moves messages to each subscriber's queue, i.e. runs an INSERT that adds relevant references to the topic message.
    Also, updates each message's is_in_sub_queue flag to indicate that it is no longer available for other subscribers.
    """

    # All the queue messages to be inserted.
    queue_msgs = []

    # Note that it is possible that there will be messages in msg_list
    # for which no subscriber will be found in the outer loop.
    # This is possible if one or more subscriptions were removed in between
    # the time when the publication was triggered and when the SQL query actually runs.
    # In such a case, such message(s) will not be delivered to a sub_key that no longer exists.

    for sub in subscriptions_by_topic:
        for msg in msg_list:

            # Enqueues the message for each subscriber
            queue_msgs.append({
                'creation_time': _float_str.format(now),
                'pub_msg_id': msg['pub_msg_id'],
                'endpoint_id': sub.endpoint_id,
                'topic_id': topic_id,
                'sub_key': sub.sub_key,
                'cluster_id': cluster_id,
                'sub_pattern_matched': msg['sub_pattern_matched'][sub.sub_key],
            })

    # Move the message to endpoint queues
    return sql_op_with_deadlock_retry(cid, 'insert_queue_messages', _insert_queue_messages, session, queue_msgs)

# ################################################################################################################################
# ################################################################################################################################
