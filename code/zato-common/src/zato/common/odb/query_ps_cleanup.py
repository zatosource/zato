# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import delete

# Zato
from zato.common import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage
from zato.common.odb.query import count, _pubsub_queue_message

# ################################################################################################################################

_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED

# ################################################################################################################################

def delete_expired(session, cluster_id, now):
    """ Deletes all expires messages from all topics.
    """
    return session.query(PubSubMessage).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.expiration_time<=now).\
        delete()

# ################################################################################################################################

def delete_delivered(session, cluster_id, _delivered=_delivered):
    """ Deletes all already delivered messages from delivery queues.
    """
    return session.query(PubSubEndpointEnqueuedMessage).\
        filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id).\
        filter(PubSubEndpointEnqueuedMessage.delivery_status==_delivered).\
        delete()

# ################################################################################################################################
