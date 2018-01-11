# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage

# ################################################################################################################################

_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED
_to_delete = PUBSUB.DELIVERY_STATUS.TO_DELETE

# ################################################################################################################################

def delete_expired(session, cluster_id, now):
    """ Deletes all expires messages from all topics.
    """
    return session.query(PubSubMessage).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.expiration_time<=now).\
        delete()

# ################################################################################################################################

def _delete_by_status(session, cluster_id, status):
    """ Deletes all messages already delivered or the ones that have been explicitly marked for deletion from delivery queues.
    """
    return session.query(PubSubEndpointEnqueuedMessage).\
        filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id).\
        filter(PubSubEndpointEnqueuedMessage.delivery_status==status).\
        delete()

# ################################################################################################################################

def delete_delivered(session, cluster_id, status=_delivered):
    """ Deletes all messages already delivered or the ones that have been explicitly marked for deletion from delivery queues.
    """
    return _delete_by_status(session, cluster_id, status)

# ################################################################################################################################

def delete_marked_deleted(session, cluster_id, status=_to_delete):
    """ Deletes all messages that have been explicitly marked for deletion from delivery queues.
    """
    return _delete_by_status(session, cluster_id, status)

# ################################################################################################################################
