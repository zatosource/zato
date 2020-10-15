# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import func

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import Cluster, PubSubEndpoint, PubSubSubscription
from zato.common.odb.query import query_wrapper

# ################################################################################################################################

_subscriber_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.SUBSCRIBER.id)

# ################################################################################################################################

def _pubsub_endpoint_summary(session, cluster_id, topic_id):
    q = session.query(
        PubSubEndpoint.id,
        PubSubEndpoint.is_active,
        PubSubEndpoint.is_internal,
        PubSubEndpoint.role,
        PubSubEndpoint.name.label('endpoint_name'),
        PubSubEndpoint.endpoint_type,
        PubSubEndpoint.last_seen,
        PubSubEndpoint.last_deliv_time,
        func.count(PubSubSubscription.id).label('subscription_count'),
        ).\
        group_by(PubSubEndpoint.id).\
        outerjoin(PubSubSubscription, PubSubEndpoint.id==PubSubSubscription.endpoint_id).\
        filter(Cluster.id==PubSubEndpoint.cluster_id).\
        filter(Cluster.id==cluster_id).\
        filter(PubSubEndpoint.role.in_(_subscriber_role))

    if topic_id:
        q = q.\
            filter(PubSubSubscription.topic_id==topic_id)

    return q

@query_wrapper
def pubsub_endpoint_summary_list(session, cluster_id, topic_id=None, needs_columns=False):
    return _pubsub_endpoint_summary(session, cluster_id, topic_id).\
        order_by(PubSubEndpoint.id)

def pubsub_endpoint_summary(session, cluster_id, endpoint_id, topic_id=None):
    return _pubsub_endpoint_summary(session, cluster_id, topic_id).\
        filter(PubSubEndpoint.id==endpoint_id).\
        one()

# ################################################################################################################################
