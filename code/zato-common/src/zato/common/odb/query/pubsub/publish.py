# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import DEBUG, getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubEndpointTopic, PubSubMessage, PubSubTopic
from zato.common.util.sql import sql_op_with_deadlock_retry

# ################################################################################################################################

logger_zato = getLogger('zato')
logger_pubsub = getLogger('zato_pubsub')

has_debug = logger_zato.isEnabledFor(DEBUG) or logger_pubsub.isEnabledFor(DEBUG)

# ################################################################################################################################

MsgInsert = PubSubMessage.__table__.insert
EndpointTopicInsert = PubSubEndpointTopic.__table__.insert
EnqueuedMsgInsert = PubSubEndpointEnqueuedMessage.__table__.insert

MsgTable = PubSubMessage.__table__
TopicTable = PubSubTopic.__table__
EndpointTable = PubSubEndpoint.__table__
EndpointTopicTable = PubSubEndpointTopic.__table__

# ################################################################################################################################

_initialized=PUBSUB.DELIVERY_STATUS.INITIALIZED

# ################################################################################################################################

def _sql_publish_with_retry(session, cid, cluster_id, topic_id, subscriptions_by_topic, gd_msg_list, now):
    """ A low-level implementation of sql_publish_with_retry.
    """
    # Publish messages - INSERT rows, each representing an individual message
    topic_messages_inserted = insert_topic_messages(session, cid, gd_msg_list)

    if has_debug:
        sub_keys_by_topic = sorted(elem.sub_key for elem in subscriptions_by_topic)
        logger_zato.info('With topic_messages_inserted `%s` `%s` `%s` `%s` `%s` `%s` `%s`',
                cid, topic_messages_inserted, cluster_id, topic_id, sub_keys_by_topic, gd_msg_list, now)

    if topic_messages_inserted:

        # Move messages to each subscriber's queue
        if subscriptions_by_topic:

            try:
                insert_queue_messages(session, cluster_id, subscriptions_by_topic, gd_msg_list, topic_id, now, cid)

                if has_debug:
                    logger_zato.info('Inserted queue messages `%s` `%s` `%s` `%s` `%s` `%s`', cid, cluster_id,
                        sub_keys_by_topic, gd_msg_list, topic_id, now)

                # No integrity error / no deadlock = all good
                return True

            except IntegrityError:

                if has_debug:
                    logger_zato.info('Caught IntegrityError (_sql_publish_with_retry) `%s` `%s`', cid, format_exc())

                # If we have an integrity error here it means that our transaction, the whole of it,
                # was rolled back - this will happen on MySQL in case in case of deadlocks which may
                # occur because delivery tasks update the table that insert_queue_messages wants to insert to.
                # We need to return False for our caller to understand that the whole transaction needs
                # to be repeated.
                return False

        else:

            if has_debug:
                logger_zato.info('No subscribers in `%s`', cid)

            # No subscribers, also good
            return True

# ################################################################################################################################

def sql_publish_with_retry(*args):
    """ Populates SQL structures with new messages for topics and their counterparts in subscriber queues.
    In case of a deadlock will retry the whole transaction, per MySQL's requirements, which rolls back
    the whole of it rather than a deadlocking statement only.
    """
    is_ok = False

    while not is_ok:

        if has_debug:
            logger_zato.info('sql_publish_with_retry -> is_ok.1:`%s`', is_ok)

        is_ok = _sql_publish_with_retry(*args)

        if has_debug:
            logger_zato.info('sql_publish_with_retry -> is_ok.2:`%s`', is_ok)

# ################################################################################################################################

def _insert_topic_messages(session, msg_list):
    """ A low-level implementation for insert_topic_messages.
    """
    session.execute(MsgInsert().values(msg_list))

# ################################################################################################################################

def insert_topic_messages(session, cid, msg_list):
    """ Publishes messages to a topic, i.e. runs an INSERT that inserts rows, one for each message.
    """
    try:
        return sql_op_with_deadlock_retry(cid, 'insert_topic_messages', _insert_topic_messages, session, msg_list)

    # Catch duplicate MsgId values sent by clients
    except IntegrityError as e:

        if has_debug:
            logger_zato.info('Caught IntegrityError (insert_topic_messages) `%s` `%s`', cid, format_exc())

        str_e = str(e)

        if 'pubsb_msg_pubmsg_id_idx' in str_e:
            raise BadRequest(cid, 'Duplicate msg_id:`{}`'.format(str_e))
        else:
            raise

# ################################################################################################################################

def _insert_queue_messages(session, queue_msgs):
    """ A low-level call to enqueue messages.
    """
    session.execute(EnqueuedMsgInsert().values(queue_msgs))

# ################################################################################################################################

def insert_queue_messages(session, cluster_id, subscriptions_by_topic, msg_list, topic_id, now, cid, _initialized=_initialized,
    _float_str=PUBSUB.FLOAT_STRING_CONVERT):
    """ Moves messages to each subscriber's queue, i.e. runs an INSERT that adds relevant references to the topic message.
    Also, updates each message's is_in_sub_queue flag to indicate that it is no longer available for other subscribers.
    """
    queue_msgs = []

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
