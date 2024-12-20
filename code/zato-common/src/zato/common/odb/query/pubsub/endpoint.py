# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import func

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import Cluster, PubSubEndpoint, PubSubSubscription
from zato.common.odb.query import query_wrapper
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Column
    from sqlalchemy.orm.query import Query
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, intnone
    intnone = intnone
    Column = Column
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

_subscriber_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.SUBSCRIBER.id)

# ################################################################################################################################
# ################################################################################################################################

def _pubsub_endpoint_summary(
    session,    # type: SASession
    cluster_id, # type: int
    topic_id    # type: intnone
) -> 'Query':
    q = session.query(
        PubSubEndpoint.id,
        PubSubEndpoint.is_active,
        PubSubEndpoint.is_internal,
        PubSubEndpoint.role,
        cast_('Column', PubSubEndpoint.name).label('endpoint_name'),
        PubSubEndpoint.endpoint_type,
        PubSubEndpoint.last_seen,
        PubSubEndpoint.last_deliv_time,
        func.count(PubSubSubscription.id).label('subscription_count'),
        ).\
        group_by(PubSubEndpoint.id).\
        outerjoin(PubSubSubscription, PubSubEndpoint.id==PubSubSubscription.endpoint_id).\
        filter(Cluster.id==PubSubEndpoint.cluster_id).\
        filter(Cluster.id==cluster_id).\
        filter(cast_('Column', PubSubEndpoint.role).in_(_subscriber_role))

    if topic_id:
        q = q.\
            filter(PubSubSubscription.topic_id==topic_id)

    return q

# ################################################################################################################################

@query_wrapper
def pubsub_endpoint_summary_list(
    session,       # type: SASession
    cluster_id,    # type: int
    topic_id=None, # type: intnone
    needs_columns=False # type: bool
) -> 'Query':
    return _pubsub_endpoint_summary(session, cluster_id, topic_id).\
        order_by(PubSubEndpoint.id)

# ################################################################################################################################

def pubsub_endpoint_summary(
    session,       # type: SASession
    cluster_id,    # type: int
    endpoint_id,   # type: int
    topic_id=None, # type: intnone
) -> 'any_':
    return _pubsub_endpoint_summary(session, cluster_id, topic_id).\
        filter(PubSubEndpoint.id==endpoint_id).\
        one()

# ################################################################################################################################
