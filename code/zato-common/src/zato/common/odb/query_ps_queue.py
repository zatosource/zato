# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription
from zato.common.odb.query import count, _pubsub_queue_message

# ################################################################################################################################

_initialized = PUBSUB.DELIVERY_STATUS.INITIALIZED
_waiting = PUBSUB.DELIVERY_STATUS.WAITING_FOR_CONFIRMATION
_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED

# ################################################################################################################################

def get_messages(session, cluster_id, sub_key, batch_size, now, _initialized=_initialized, _waiting=_waiting):
    """ Returns up to batch_size messages for input sub_key and mark them as being delivered.
    """
    # First, get all messages but note it is SELECT FOR UPDATE
    messages = _pubsub_queue_message(session, cluster_id).\
        filter(PubSubSubscription.sub_key==sub_key).\
        filter(PubSubEndpointEnqueuedMessage.delivery_status==_initialized).\
        filter(PubSubMessage.expiration_time>=now).\
        with_for_update().\
        order_by(PubSubMessage.ext_pub_time.desc()).\
        limit(batch_size).\
        all()

    # Now, within the same transaction, update their delivery status to indicate they are being delivered
    msg_id_list = [elem.msg_id for elem in messages]

    if msg_id_list:
        session.execute(
            update(PubSubEndpointEnqueuedMessage).\
            values({
                'delivery_status': _waiting,
                'delivery_time': now,
                'delivery_count': PubSubEndpointEnqueuedMessage.__table__.c.delivery_count + 1,
                }).\
            where(PubSubEndpointEnqueuedMessage.cluster_id).\
            where(PubSubEndpointEnqueuedMessage.pub_msg_id.in_(msg_id_list))
        )

    # Return all messages fetched - our caller will commit the transaction thus releasing the FOR UPDATE lock
    return messages

# ################################################################################################################################

def acknowledge_delivery(session, cluster_id, sub_key, msg_id_list, now, _delivered=_delivered):
    """ Confirms delivery of all messages from msg_id_list.
    """
    session.execute(
        update(PubSubEndpointEnqueuedMessage).\
        values({
            'delivery_status': _delivered,
            'delivery_time': now,
            }).\
        where(PubSubSubscription.sub_key==sub_key).\
        where(PubSubEndpointEnqueuedMessage.cluster_id).\
        where(PubSubEndpointEnqueuedMessage.subscription_id==PubSubSubscription.id).\
        where(PubSubEndpointEnqueuedMessage.delivery_status==_waiting).\
        where(PubSubEndpointEnqueuedMessage.pub_msg_id.in_(msg_id_list))
    )

# ################################################################################################################################

def get_queue_depth_by_sub_key(session, cluster_id, sub_key, now):
    """ Returns queue depth for a given sub_key - does not include messages expired, in staging, or already delivered.
    """
    current_q = session.query(PubSubEndpointEnqueuedMessage.id).\
        filter(PubSubSubscription.id==PubSubEndpointEnqueuedMessage.subscription_id).\
        filter(PubSubEndpointEnqueuedMessage.is_in_staging != True).\
        filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
        filter(PubSubMessage.expiration_time>=now).\
        filter(PubSubSubscription.sub_key==sub_key).\
        filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id)

    return count(session, current_q)

# ################################################################################################################################
