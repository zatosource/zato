# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import and_, exists, insert, update
from sqlalchemy.sql import expression as expr

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpointEnqueuedMessage, PubSubMessage, PubSubSubscription, WebSocketSubscription
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################

MsgTable = PubSubMessage.__table__

# ################################################################################################################################

_initialized = PUBSUB.DELIVERY_STATUS.INITIALIZED

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

def add_wsx_subscription(session, cluster_id, is_internal, sub_key, ext_client_id, ws_channel_id, sub_id):
    """ Adds an object representing a subscription of a WebSockets client.
    """
    wsx_sub = WebSocketSubscription()
    wsx_sub.is_internal = is_internal or False
    wsx_sub.sub_key = sub_key
    wsx_sub.ext_client_id = ext_client_id
    wsx_sub.channel_id = ws_channel_id
    wsx_sub.cluster_id = cluster_id
    wsx_sub.subscription_id = sub_id
    session.add(wsx_sub)

    return wsx_sub

# ################################################################################################################################

def add_subscription(session, cluster_id, sub_key, ctx):
    """ Adds an object representing a subscription regardless of the underlying protocol.
    """
    # Common
    ps_sub = PubSubSubscription()

    ps_sub.cluster_id = ctx.cluster_id
    ps_sub.server_id = ctx.server_id
    ps_sub.topic_id = ctx.topic.id
    ps_sub.is_internal = ctx.is_internal
    ps_sub.is_staging_enabled = ctx.is_staging_enabled
    ps_sub.creation_time = ctx.creation_time
    ps_sub.sub_key = sub_key
    ps_sub.sub_pattern_matched = ctx.sub_pattern_matched
    ps_sub.has_gd = ctx.has_gd
    ps_sub.active_status = ctx.active_status
    ps_sub.endpoint_type = ctx.endpoint_type
    ps_sub.endpoint_id = ctx.endpoint_id
    ps_sub.delivery_method = ctx.delivery_method
    ps_sub.delivery_data_format = ctx.delivery_data_format
    ps_sub.delivery_batch_size = ctx.delivery_batch_size
    ps_sub.wrap_one_msg_in_list = ctx.wrap_one_msg_in_list if ctx.wrap_one_msg_in_list is not None else True
    ps_sub.delivery_max_retry = ctx.delivery_max_retry
    ps_sub.delivery_err_should_block = ctx.delivery_err_should_block if ctx.delivery_err_should_block is not None else True
    ps_sub.wait_sock_err = ctx.wait_sock_err
    ps_sub.wait_non_sock_err = ctx.wait_non_sock_err
    ps_sub.ext_client_id = ctx.ext_client_id

    # AMQP
    ps_sub.amqp_exchange = ctx.amqp_exchange
    ps_sub.amqp_routing_key = ctx.amqp_routing_key
    ps_sub.out_amqp_id = ctx.out_amqp_id

    # Local files
    ps_sub.files_directory_list = ctx.files_directory_list

    # FTP
    ps_sub.ftp_directory_list = ctx.ftp_directory_list

    # REST/SOAP
    ps_sub.security_id = ctx.security_id
    ps_sub.out_http_soap_id = ctx.out_http_soap_id
    ps_sub.out_http_method = ctx.out_http_method

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

    session.add(ps_sub)

    return ps_sub

# ################################################################################################################################

def move_messages_to_sub_queue(session, cluster_id, topic_id, endpoint_id, sub_pattern_matched, sub_key, pub_time_max,
    _initialized=_initialized):
    """ Move all unexpired messages from topic to a given subscriber's queue. This method must be called with a global lock
    held for topic because it carries out its job through a couple of non-atomic queries.
    """
    enqueued_id_subquery = session.query(
        PubSubEndpointEnqueuedMessage.pub_msg_id
        ).\
        filter(PubSubEndpointEnqueuedMessage.sub_key==sub_key)

    now = utcnow_as_ms()

    # SELECT statement used by the INSERT below finds all messages for that topic
    # that haven't expired yet.
    select_messages = session.query(
        PubSubMessage.pub_msg_id,
        PubSubMessage.topic_id,
        expr.bindparam('creation_time', now),
        expr.bindparam('endpoint_id', endpoint_id),
        expr.bindparam('sub_pattern_matched', sub_pattern_matched),
        expr.bindparam('sub_key', sub_key),
        expr.bindparam('is_in_staging', False),
        expr.bindparam('cluster_id', cluster_id),
        ).\
        filter(PubSubMessage.topic_id==topic_id).\
        filter(PubSubMessage.cluster_id==cluster_id).\
        filter(PubSubMessage.expiration_time > pub_time_max).\
        filter(~PubSubMessage.is_in_sub_queue).\
        filter(PubSubMessage.pub_msg_id.notin_(enqueued_id_subquery))

    # All message IDs that are available in topic for that subscriber, if there are any at all.
    # In theory, it is not required to pull all the messages to build the list in Python, but this is a relatively
    # efficient operation because there won't be that many data returned yet it allows us to make sure
    # the INSERT and UPDATE below are issued only if truly needed.
    msg_ids = [elem.pub_msg_id for elem in select_messages.all()]

    if msg_ids:

        # INSERT references to topic's messages in the subscriber's queue.
        insert_messages = insert(PubSubEndpointEnqueuedMessage).\
            from_select((
                PubSubEndpointEnqueuedMessage.pub_msg_id,
                PubSubEndpointEnqueuedMessage.topic_id,
                expr.column('creation_time'),
                expr.column('endpoint_id'),
                expr.column('sub_pattern_matched'),
                expr.column('sub_key'),
                expr.column('is_in_staging'),
                expr.column('cluster_id'),
                ), select_messages)

        # Move messages to subscriber's queue
        session.execute(insert_messages)

        # Indicate that all the messages are being delivered to the subscriber which means that no other
        # subscriber will ever receive them. Note that we are changing the status only for the messages pertaining
        # to the current subscriber without ever touching messages reiceved by any other one.

        session.execute(
            update(MsgTable).\
            values({
                'is_in_sub_queue': True,
                }).\
            where(and_(
                MsgTable.c.pub_msg_id.in_(msg_ids),
                ~MsgTable.c.is_in_sub_queue
            ))
        )

# ################################################################################################################################
