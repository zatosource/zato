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

def add_subscription(session, cluster_id, ctx):
    """ Adds an object representing a subscription regardless of the underlying protocol.
    """
    # Common
    ps_sub = PubSubSubscription()

    ps_sub.cluster_id = ctx.cluster_id
    ps_sub.server_id = ctx.server_id
    ps_sub.topic_id = ctx.topic.id
    ps_sub.is_internal = ctx.is_internal
    ps_sub.creation_time = ctx.creation_time
    ps_sub.sub_key = ctx.sub_key
    ps_sub.pattern_matched = ctx.pattern_matched
    ps_sub.has_gd = ctx.has_gd
    ps_sub.active_status = ctx.active_status
    ps_sub.endpoint_type = ctx.endpoint_type
    ps_sub.endpoint_id = ctx.endpoint_id
    ps_sub.delivery_method = ctx.delivery_method
    ps_sub.delivery_data_format = ctx.delivery_data_format
    ps_sub.delivery_batch_size = ctx.delivery_batch_size
    ps_sub.wrap_one_msg_in_list = ctx.wrap_one_msg_in_list
    ps_sub.delivery_max_retry = ctx.delivery_max_retry
    ps_sub.delivery_err_should_block = ctx.delivery_err_should_block
    ps_sub.wait_sock_err = ctx.wait_sock_err
    ps_sub.wait_non_sock_err = ctx.wait_non_sock_err
    ps_sub.ext_client_id = ctx.ext_client_id

    # AMQP
    ps_sub.amqp_exchange = ctx.amqp_exchange
    ps_sub.amqp_routing_key = ctx.amqp_routing_key

    # Local files
    ps_sub.files_directory_list = ctx.files_directory_list

    # FTP
    ps_sub.ftp_directory_list = ctx.ftp_directory_list

    # REST/SOAP
    ps_sub.security_id = ctx.security_id
    ps_sub.out_http_soap_id = ctx.out_http_soap_id

    # Services
    ps_sub.service_id = ctx.service_id

    # SMS - Twilio
    ps_sub.sms_twilio_from = ctx.sms_twilio_from
    ps_sub.sms_twilio_to_list = ctx.sms_twilio_to_list
    ps_sub.smtp_is_html = ctx.smtp_is_html
    ps_sub.smtp_subject = ctx.smtp_subject
    ps_sub.smtp_from = ctx.smtp_from
    ps_sub.smtp_to_list = ctx.smtp_to_list
    ps_sub.smtp_body = ctx.smtp_body

    # WebSockets
    ps_sub.ws_channel_id = ctx.ws_channel_id
    ps_sub.ws_channel_name = ctx.ws_channel_name
    ps_sub.ws_pub_client_id = ctx.ws_pub_client_id
    ps_sub.sql_ws_client_id = ctx.sql_ws_client_id

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

