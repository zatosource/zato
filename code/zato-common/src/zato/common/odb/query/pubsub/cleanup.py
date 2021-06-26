# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import true as sa_true

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage

# ################################################################################################################################

_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED
_to_delete = PUBSUB.DELIVERY_STATUS.TO_DELETE

# ################################################################################################################################

def delete_msg_delivered(session, cluster_id, topic_id):
    """ Deletes from topics all messages that have been delivered from their queues.
    """
    # When a message is published and there are subscribers for it, its PubSubMessage.is_in_sub_queue attribute
    # is set to True and a reference to that message is stored in PubSubEndpointEnqueuedMessage. Then, once the message
    # is delivered to all subscribers, a background process calling delete_enq_delivered deletes all the references.
    # Therefore, we can delete all PubSubMessage that have is_in_sub_queue = True because it means that there must have
    # been subscribers to it and, seeing as there are no references to it anymore, it means that they must have been
    # already deleted, so we can safely delete the PubSubMessage itself.

    enqueued_subquery = session.query(PubSubMessage.pub_msg_id).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.topic_id==topic_id).\
        filter(PubSubMessage.is_in_sub_queue==sa_true()).\
        filter(PubSubMessage.pub_msg_id==PubSubEndpointEnqueuedMessage.pub_msg_id)

    return session.query(PubSubMessage).\
        filter(PubSubMessage.pub_msg_id.notin_(enqueued_subquery)).\
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
