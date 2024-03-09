# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import operator
from logging import getLogger

# SQLAlchemy
from sqlalchemy import and_, delete, func, or_, select

# Zato
from zato.common.odb.model import PubSubEndpoint, PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, PubSubTopic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.orm.query import Query
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_pubsub.sql')

# ################################################################################################################################
# ################################################################################################################################

QueueTable   = PubSubEndpointEnqueuedMessage.__table__
MsgTable = PubSubMessage.__table__

# ################################################################################################################################
# ################################################################################################################################

def get_subscriptions(
    task_id:'str',
    session:'SASession',
    topic_id: 'int',
    topic_name: 'str',
    max_last_interaction_time:'float',
    topic_max_last_interaction_time_dt:'datetime',
    topic_max_last_interaction_time_source:'str'
    ) -> 'anylist':

    msg = '%s: Getting subscriptions for topic `%s` (id:%s) with max_last_interaction_time `%s` -> %s (s:%s)'
    logger.info(msg, task_id, topic_name, topic_id,
        max_last_interaction_time, topic_max_last_interaction_time_dt, topic_max_last_interaction_time_source)

    result = session.query(
        PubSubSubscription.id,
        PubSubSubscription.sub_key,
        PubSubSubscription.ext_client_id,
        PubSubSubscription.last_interaction_time,
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubEndpoint.id.label('endpoint_id'),
        PubSubTopic.opaque1.label('topic_opaque'),
        ).\
        filter(PubSubSubscription.topic_id == topic_id).\
        filter(PubSubSubscription.topic_id == PubSubTopic.id).\
        filter(PubSubSubscription.endpoint_id == PubSubEndpoint.id).\
        filter(PubSubEndpoint.is_internal.is_(False)).\
        filter(or_(
            PubSubSubscription.last_interaction_time < max_last_interaction_time,
            PubSubSubscription.last_interaction_time.is_(None),
        )).\
        order_by(PubSubSubscription.last_interaction_time.asc()).\
        all()

    return result

# ################################################################################################################################
# ################################################################################################################################

def get_topic_messages_with_max_retention_reached(
    task_id:'str',
    session:'SASession',
    topic_id:'int',
    topic_name:'str',
    max_pub_time_dt:'datetime',
    max_pub_time_float:'float',
    ) -> 'anylist':

    logger.info('%s: Looking for messages with max. retention reached for topic `%s` (%s -> %s)',
        task_id, topic_name, max_pub_time_float, max_pub_time_dt)

    result = session.query(
        PubSubMessage.pub_msg_id,
        ).\
        filter(PubSubMessage.topic_id == topic_id).\
        filter(PubSubMessage.pub_time < max_pub_time_float).\
        all()

    return result

# ################################################################################################################################
# ################################################################################################################################

def _get_topic_messages_by_in_how_many_queues(
    session:'SASession',
    topic_id:'int',
    queue_len_operator: 'any_',
    queue_len: 'int',
    ) -> 'Query':

    # If it is zero, it means that there are no subscribers for a given message.
    # Otherwise, the message is in at least one subscription queue.
    in_how_many_queues = func.count(PubSubEndpointEnqueuedMessage.pub_msg_id).label('in_how_many_queues')

    #
    # This is used to build conditions representing two cases:
    #
    # 1) having(in_how_many_queues == 0) # No subscribers for message
    # 2) having(in_how_many_queues >= 1) # At least one subscriber for message
    #
    #
    condition = queue_len_operator(in_how_many_queues, queue_len)

    query = session.query(
        PubSubMessage.pub_msg_id,
        ).\
        group_by(PubSubMessage.pub_msg_id).\
        outerjoin(PubSubEndpointEnqueuedMessage, PubSubMessage.id==PubSubEndpointEnqueuedMessage.pub_msg_id).\
        having(condition).\
        filter(PubSubMessage.topic_id == topic_id)

    return query

# ################################################################################################################################
# ################################################################################################################################

def get_topic_messages_without_subscribers(
    task_id:'str',
    session:'SASession',
    topic_id:'int',
    topic_name:'str',
    max_pub_time_dt:'datetime',
    max_pub_time_float:'float',
    ) -> 'anylist':

    logger.info('%s: Looking for messages without subscribers for topic `%s` (%s -> %s)',
        task_id, topic_name, max_pub_time_float, max_pub_time_dt)

    #
    # We are building a query condition of this form: having(in_how_many_queues == 0)
    #
    queue_len_operator = operator.eq # eq = equal
    queue_len = 0

    # Build a base query ..
    query = _get_topic_messages_by_in_how_many_queues(
        session,
        topic_id,
        queue_len_operator,
        queue_len
    )

    # Add our own condition around the max. publication time - we need it because we do not want
    # to return messages that have not reached their retention time yet. E.g. if a message was published
    # during a cleanup procedure, it may still see its subscriber in the next N seconds,
    # which is why we cannot return it. If it never receives a subscriber, or if its max. retention time
    # is eventually reached, it will be cleaned up in another pass of the cleanup procedure.
    query = query.\
        filter(PubSubMessage.pub_time < max_pub_time_float)

    # .. obtain the result  ..
    result = query.all()

    # .. and return it to the caller.
    return result

# ################################################################################################################################
# ################################################################################################################################

def get_topic_messages_already_expired(
    task_id:'str',
    session:'SASession',
    topic_id:'int',
    topic_name:'str',
    max_pub_time_dt:'datetime',
    max_pub_time_float:'float',
    ) -> 'anylist':

    logger.info('%s: Looking for already expired messages for topic `%s` (%s -> %s)',
        task_id, topic_name, max_pub_time_float, max_pub_time_dt)

    # Build a query to find all the expired messages for the topic ..
    query = select([
        MsgTable.c.pub_msg_id,
        ]).\
        where(and_(
            MsgTable.c.topic_id == topic_id,
            MsgTable.c.expiration_time < max_pub_time_float,
        ))

    # .. obtain the result  ..
    result = session.execute(query).fetchall()

    # .. and return it to the caller.
    return result

# ################################################################################################################################
# ################################################################################################################################

def delete_queue_messages(session:'SASession', msg_id_list:'strlist') -> 'None':

    logger.info('Deleting %d queue message(s): %s', len(msg_id_list), msg_id_list)

    session.execute(
        delete(QueueTable).\
        where(
            QueueTable.c.pub_msg_id.in_(msg_id_list),
        )
    )

# ################################################################################################################################
# ################################################################################################################################

def delete_topic_messages(session:'SASession', msg_id_list:'strlist') -> 'None':

    logger.info('Deleting %d topic message(s): %s', len(msg_id_list), msg_id_list)

    session.execute(
        delete(MsgTable).\
        where(
            MsgTable.c.pub_msg_id.in_(msg_id_list),
        )
    )

# ################################################################################################################################
# ################################################################################################################################
