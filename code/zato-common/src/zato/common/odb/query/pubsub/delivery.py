# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# SQLAlchemy
from sqlalchemy import update

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpoint, PubSubMessage, PubSubEndpointEnqueuedMessage, PubSubSubscription, Server, \
     WebSocketClient, WebSocketClientPubSubKeys

logger = getLogger('zato_pubsub.sql')

# ################################################################################################################################

_initialized = PUBSUB.DELIVERY_STATUS.INITIALIZED
_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED
_wsx = PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

# ################################################################################################################################

sql_messages_columns = (
    PubSubMessage.pub_msg_id,
    PubSubMessage.pub_correl_id,
    PubSubMessage.in_reply_to,
    PubSubMessage.published_by_id,
    PubSubMessage.ext_client_id,
    PubSubMessage.group_id,
    PubSubMessage.position_in_group,
    PubSubMessage.pub_time,
    PubSubMessage.ext_pub_time,
    PubSubMessage.data,
    PubSubMessage.mime_type,
    PubSubMessage.priority,
    PubSubMessage.expiration,
    PubSubMessage.expiration_time,
    PubSubMessage.size,
    PubSubMessage.user_ctx,
    PubSubMessage.zato_ctx,
    PubSubMessage.opaque1,
    PubSubEndpointEnqueuedMessage.id.label('endp_msg_queue_id'),
    PubSubEndpointEnqueuedMessage.sub_key,
    PubSubEndpointEnqueuedMessage.sub_pattern_matched,
)

sql_msg_id_columns = (
    PubSubMessage.pub_msg_id,
)

# ################################################################################################################################

def _get_base_sql_msg_query(session, columns, sub_key_list, pub_time_max, cluster_id, _float_str=PUBSUB.FLOAT_STRING_CONVERT):
    return session.query(*columns).\
        filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
        filter(PubSubEndpointEnqueuedMessage.sub_key.in_(sub_key_list)).\
        filter(PubSubEndpointEnqueuedMessage.delivery_status==_initialized).\
        filter(PubSubMessage.expiration_time > _float_str.format(pub_time_max)).\
        filter(PubSubMessage.cluster_id==cluster_id)

# ################################################################################################################################

def _get_sql_msg_data_by_sub_key(session, cluster_id, sub_key_list, last_sql_run, pub_time_max, columns, ignore_list=None,
    needs_result=True, _initialized=_initialized, _float_str=PUBSUB.FLOAT_STRING_CONVERT):
    """ Returns all SQL messages queued up for a given sub_key that are not being delivered
    or have not been delivered already.
    """
    logger.info('Getting GD messages for `%s` last_run:%r pub_time_max:%r needs_result:%d', sub_key_list, last_sql_run,
        pub_time_max, int(needs_result))

    query = _get_base_sql_msg_query(session, columns, sub_key_list, pub_time_max, cluster_id)

    # If there is the last SQL run time given, it means that we have to fetch all messages
    # enqueued for that subscriber since that time ..
    if last_sql_run:
        query = query.\
            filter(PubSubEndpointEnqueuedMessage.creation_time > _float_str.format(last_sql_run))

    query = query.\
        filter(PubSubEndpointEnqueuedMessage.creation_time <= _float_str.format(pub_time_max))

    if ignore_list:
        query = query.\
            filter(PubSubEndpointEnqueuedMessage.id.notin_(ignore_list))

    query = query.\
        order_by(PubSubMessage.priority.desc()).\
        order_by(PubSubMessage.ext_pub_time).\
        order_by(PubSubMessage.pub_time)

    return query.all() if needs_result else query

# ################################################################################################################################

def get_sql_messages_by_sub_key(session, cluster_id, sub_key_list, last_sql_run, pub_time_max, ignore_list):
    return _get_sql_msg_data_by_sub_key(session, cluster_id, sub_key_list, last_sql_run, pub_time_max,
        sql_messages_columns, ignore_list)

# ################################################################################################################################

def get_sql_messages_by_msg_id_list(session, cluster_id, sub_key, pub_time_max, msg_id_list):
    query = _get_base_sql_msg_query(session, sql_messages_columns, [sub_key], pub_time_max, cluster_id)
    return query.\
        filter(PubSubEndpointEnqueuedMessage.pub_msg_id.in_(msg_id_list))

# ################################################################################################################################

def get_sql_msg_ids_by_sub_key(session, cluster_id, sub_key, last_sql_run, pub_time_max):
    return _get_sql_msg_data_by_sub_key(session, cluster_id, [sub_key], last_sql_run, pub_time_max, sql_msg_id_columns,
        needs_result=False)

# ################################################################################################################################

def confirm_pubsub_msg_delivered(session, cluster_id, sub_key, delivered_pub_msg_id_list, now, _delivered=_delivered):
    """ Returns all SQL messages queued up for a given sub_key.
    """
    session.execute(
        update(PubSubEndpointEnqueuedMessage).\
        values({
            'delivery_status': _delivered,
            'delivery_time': now
            }).\
        where(PubSubEndpointEnqueuedMessage.pub_msg_id.in_(delivered_pub_msg_id_list)).\
        where(PubSubEndpointEnqueuedMessage.sub_key==sub_key)
    )

# ################################################################################################################################

def get_delivery_server_for_sub_key(session, cluster_id, sub_key, is_wsx):
    """ Returns information about which server handles delivery tasks for input sub_key, the latter must exist in DB.
    Assumes that sub_key belongs to a non-WSX endpoint and then checks WebSockets in case the former query founds
    no matching server.
    """
    # Sub key belongs to a WebSockets client ..
    if is_wsx:
        return session.query(
            Server.id.label('server_id'),
            Server.name.label('server_name'),
            Server.cluster_id,
            ).\
            filter(WebSocketClient.server_id==Server.id).\
            filter(WebSocketClient.cluster_id==cluster_id).\
            filter(WebSocketClient.id==WebSocketClientPubSubKeys.client_id).\
            filter(WebSocketClientPubSubKeys.sub_key==sub_key).\
            first()

    # .. otherwise, it is a REST, SOAP or another kind of client, but for sure it's not WebSockets.
    else:
        return session.query(
            Server.id.label('server_id'),
            Server.name.label('server_name'),
            Server.cluster_id,
            PubSubEndpoint.endpoint_type,
            ).\
            filter(Server.id==PubSubSubscription.server_id).\
            filter(PubSubSubscription.sub_key==sub_key).\
            filter(PubSubSubscription.endpoint_id==PubSubEndpoint.id).\
            filter(PubSubSubscription.cluster_id==cluster_id).\
            first()

# ################################################################################################################################
