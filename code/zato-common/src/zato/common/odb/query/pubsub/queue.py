# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import func, update

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription
from zato.common.odb.query import count, _pubsub_queue_message
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import anylist, intlist, strlistempty
    intlist = intlist
    strlistempty = strlistempty
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

PubSubEnqMsg = PubSubEndpointEnqueuedMessage

# ################################################################################################################################
# ################################################################################################################################

_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED
_initialized = PUBSUB.DELIVERY_STATUS.INITIALIZED
_to_delete = PUBSUB.DELIVERY_STATUS.TO_DELETE
_waiting = PUBSUB.DELIVERY_STATUS.WAITING_FOR_CONFIRMATION

# ################################################################################################################################
# ################################################################################################################################

def get_messages(
    session,     # type: SASession
    cluster_id,  # type: int
    sub_key,     # type: str
    batch_size,  # type: int
    now          # type: float
) -> 'anylist':
    """ Returns up to batch_size messages for input sub_key and mark them as being delivered.
    """
    # First, get all messages but note it is SELECT FOR UPDATE
    messages = _pubsub_queue_message(session, cluster_id).\
        filter(PubSubSubscription.sub_key==sub_key).\
        filter(PubSubEnqMsg.delivery_status==_initialized).\
        filter(PubSubMessage.expiration_time>=now).\
        with_for_update().\
        order_by(PubSubMessage.ext_pub_time.desc()).\
        limit(batch_size).\
        all()

    # Now, within the same transaction, update their delivery status to indicate they are being delivered
    msg_id_list = [elem.msg_id for elem in messages]

    if msg_id_list:
        session.execute(
            update(PubSubEnqMsg).\
            values({
                'delivery_status': _waiting,
                'delivery_time': now,
                'delivery_count': PubSubEnqMsg.__table__.c.delivery_count + 1,
            }).\
            where(PubSubEnqMsg.cluster_id).\
            where(PubSubEnqMsg.pub_msg_id.in_(msg_id_list))
        )

    # Return all messages fetched - our caller will commit the transaction thus releasing the FOR UPDATE lock
    return messages

# ################################################################################################################################

def _set_delivery_status(
    session,     # type: SASession
    cluster_id,  # type: int
    sub_key,     # type: str
    msg_id_list, # type: intlist
    now,         # type: float
    status       # type: int
) -> 'None':
    session.execute(
        update(PubSubEnqMsg).\
        values({
            'delivery_status': status,
            'delivery_time': now,
        }).\
        where(PubSubEnqMsg.cluster_id).\
        where(PubSubEnqMsg.sub_key==sub_key).\
        where(PubSubEnqMsg.pub_msg_id.in_(msg_id_list))
    )

# ################################################################################################################################

def set_to_delete(
    session,     # type: SASession
    cluster_id,  # type: int
    sub_key,     # type: str
    msg_id_list, # type: strlistempty
    now,         # type: float
    status=_to_delete # type: int
) -> 'None':
    """ Marks all input messages as to be deleted.
    """
    _set_delivery_status(session, cluster_id, sub_key, msg_id_list, now, status)

# ################################################################################################################################

def acknowledge_delivery(
    session,     # type: SASession
    cluster_id,  # type: int
    sub_key,     # type: str
    msg_id_list, # type: intlist
    now,         # type: float
    status=_delivered # type: int
) -> 'None':
    """ Confirms delivery of all messages from msg_id_list.
    """
    _set_delivery_status(session, cluster_id, sub_key, msg_id_list, now, status)

# ################################################################################################################################

def get_queue_depth_by_sub_key(
    session,    # type: SASession
    cluster_id, # type: int
    sub_key,    # type: str
    now         # type: float
) -> 'int':
    """ Returns queue depth for a given sub_key - does not include messages expired, in staging, or already delivered.
    """
    current_q = session.query(PubSubEnqMsg.id).\
        filter(PubSubSubscription.sub_key==PubSubEnqMsg.sub_key).\
        filter(PubSubEnqMsg.is_in_staging != True).\
        filter(PubSubEnqMsg.pub_msg_id==PubSubMessage.pub_msg_id).\
        filter(PubSubMessage.expiration_time>=now).\
        filter(PubSubSubscription.sub_key==sub_key).\
        filter(PubSubEnqMsg.cluster_id==cluster_id) # noqa: E712

    return count(session, current_q)

# ################################################################################################################################

def get_queue_depth_by_topic_id_list(
    session,       # type: SASession
    cluster_id,    # type: int
    topic_id_list  # type: intlist
) -> 'anylist':
    """ Returns queue depth for a given sub_key - does not include messages expired, in staging, or already delivered.
    """
    return session.query(PubSubEnqMsg.topic_id, func.count(PubSubEnqMsg.topic_id)).\
        filter(PubSubEnqMsg.topic_id.in_(topic_id_list)).\
        filter(PubSubEnqMsg.cluster_id==cluster_id).\
        filter(PubSubEnqMsg.delivery_status==_initialized).\
        filter(PubSubEnqMsg.pub_msg_id==PubSubMessage.pub_msg_id).\
        filter(PubSubMessage.expiration_time>=utcnow_as_ms()).\
        group_by(PubSubMessage.topic_id).\
        all()

# ################################################################################################################################
