# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import true as sa_true

# Zato
from zato.common import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage

# ################################################################################################################################

_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED
_to_delete = PUBSUB.DELIVERY_STATUS.TO_DELETE

# ################################################################################################################################

def delete_msg_delivered(session, cluster_id, topic_id, status=_delivered):
    """ Deletes from topics all messages that have been delivered from their queues.
    """
    enqueued_subquery = session.query(PubSubMessage.pub_msg_id).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.is_in_sub_queue==sa_true()).\
        filter(PubSubMessage.pub_msg_id==PubSubEndpointEnqueuedMessage.pub_msg_id).\
        filter(PubSubEndpointEnqueuedMessage.delivery_status==status)

    if topic_id:
        enqueued_subquery = enqueued_subquery.filter(PubSubMessage.topic_id==topic_id)

    return session.query(PubSubMessage).\
        filter(PubSubMessage.pub_msg_id.in_(enqueued_subquery)).\
        delete(synchronize_session=False)

# ################################################################################################################################

def delete_msg_expired(session, cluster_id, topic_id, now):
    """ Deletes all expired messages from all topics.
    """
    q = session.query(PubSubMessage).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.expiration_time<=now)

    if topic_id:
        q = q.filter(PubSubMessage.topic_id==topic_id)

    return q.delete()

# ################################################################################################################################

def _delete_enq_msg_by_status(session, cluster_id, topic_id, status):
    """ Deletes all messages already delivered or the ones that have been explicitly marked for deletion from delivery queues.
    """
    q = session.query(PubSubEndpointEnqueuedMessage).\
        filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id).\
        filter(PubSubEndpointEnqueuedMessage.delivery_status==status)

    if topic_id:
        q = q.filter(PubSubEndpointEnqueuedMessage.topic_id==topic_id)

    return q.delete()

# ################################################################################################################################

def delete_enq_delivered(session, cluster_id, topic_id, status=_delivered):
    """ Deletes all messages already delivered or the ones that have been explicitly marked for deletion from delivery queues.
    """
    return _delete_enq_msg_by_status(session, cluster_id, topic_id, status)

# ################################################################################################################################

def delete_enq_marked_deleted(session, cluster_id, topic_id, status=_to_delete):
    """ Deletes all messages that have been explicitly marked for deletion from delivery queues.
    """
    return _delete_enq_msg_by_status(session, cluster_id, topic_id, status)

# ################################################################################################################################
