# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import and_, exists, insert
from sqlalchemy.sql import expression as expr, func

# Zato
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, WebSocketSubscription

# ################################################################################################################################

def has_subscription(session, cluster_id, topic_id, endpoint_id):
    """ Returns a boolean flag indicating whether input endpoint has subscription to a given topic.
    """
    return session.query(exists().where(and_(
        PubSubSubscription.endpoint_id==endpoint_id,
            PubSubSubscription.topic_id==topic_id,
            PubSubSubscription.cluster_id==cluster_id,
            ))).\
        scalar()

# ################################################################################################################################

def add_wsx_subscription(session, cluster_id, is_internal, sub_key, ext_client_id, ws_channel_id):
    """ Adds an object representing a subscription of a WebSockets client.
    """
    ws_sub = WebSocketSubscription()
    ws_sub.is_internal = is_internal
    ws_sub.sub_key = sub_key
    ws_sub.ext_client_id = ext_client_id
    ws_sub.channel_id = ws_channel_id
    ws_sub.cluster_id = cluster_id
    session.add(ws_sub)

    return ws_sub

# ################################################################################################################################

def add_subscription(session, cluster_id, active_status, is_internal, creation_time, pattern_matched, sub_key, has_gd, topic_id,
    endpoint_id, delivery_method, delivery_data_format, deliver_to, deliver_by, delivery_group_size, ws_channel_id, ws_sub):
    """ Adds an object representing a subscription regardless of the underlying protocol.
    """
    ps_sub = PubSubSubscription()
    ps_sub.active_status = active_status
    ps_sub.is_internal = is_internal
    ps_sub.creation_time = creation_time
    ps_sub.pattern_matched = pattern_matched
    ps_sub.sub_key = sub_key
    ps_sub.has_gd = has_gd
    ps_sub.topic_id = topic_id
    ps_sub.endpoint_id = endpoint_id
    ps_sub.delivery_method = delivery_method
    ps_sub.delivery_data_format = delivery_data_format
    ps_sub.delivery_endpoint = deliver_to
    ps_sub.deliver_by = deliver_by
    ps_sub.delivery_group_size = delivery_group_size
    ps_sub.ws_channel_id = ws_channel_id
    ps_sub.ws_sub = ws_sub
    ps_sub.cluster_id = cluster_id
    session.add(ps_sub)

    return ps_sub

# ################################################################################################################################

def move_messages_to_sub_queue(session, cluster_id, topic_id, endpoint_id, ps_sub_id, now):
    """ Move all unexpired messages from topic to a given subscriber's queue and returns the number of messages moved.
    """

    # SELECT statement used by the INSERT below finds all messages for that topic
    # that haven't expired yet.
    select_messages = session.query(
        PubSubMessage.pub_msg_id, PubSubMessage.topic_id,
        expr.bindparam('creation_time', now),
        expr.bindparam('delivery_count', 0),
        expr.bindparam('endpoint_id', endpoint_id),
        expr.bindparam('subscription_id', ps_sub_id),
        expr.bindparam('has_gd', False),
        expr.bindparam('is_in_staging', False),
        expr.bindparam('cluster_id', cluster_id),
        ).\
        filter(PubSubMessage.topic_id==topic_id).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.expiration_time > now)

    # INSERT references to topic's messages in the subscriber's queue.
    insert_messages = insert(PubSubEndpointEnqueuedMessage).\
        from_select((
            PubSubEndpointEnqueuedMessage.pub_msg_id,
            PubSubEndpointEnqueuedMessage.topic_id,
            expr.column('creation_time'),
            expr.column('delivery_count'),
            expr.column('endpoint_id'),
            expr.column('subscription_id'),
            expr.column('has_gd'),
            expr.column('is_in_staging'),
            expr.column('cluster_id'),
            ), select_messages)

    # Commit changes to subscriber's queue
    session.execute(insert_messages)

    # Get the number of messages moved to let the subscriber know
    # how many there are available initially.
    moved_q = session.query(PubSubEndpointEnqueuedMessage.id).\
        filter(PubSubEndpointEnqueuedMessage.subscription_id==ps_sub_id).\
        filter(PubSubEndpointEnqueuedMessage.cluster_id==cluster_id)

    total_moved_q = moved_q.statement.with_only_columns([func.count()]).order_by(None)
    total_moved = moved_q.session.execute(total_moved_q).scalar()

    return total_moved

# ################################################################################################################################
