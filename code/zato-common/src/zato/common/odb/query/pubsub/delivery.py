# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# SQLAlchemy
from sqlalchemy import update
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import expression as expr

# Bunch
from bunch import Bunch

# Zato
from zato.common import PUBSUB
from zato.common.odb.model import ChannelWebSocket, PubSubEndpoint, PubSubMessage, PubSubEndpointEnqueuedMessage, \
     PubSubSubscription, Server, WebSocketClient, WebSocketClientPubSubKeys

# ################################################################################################################################

_initialized = PUBSUB.DELIVERY_STATUS.INITIALIZED
_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED
_wsx = PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

# ################################################################################################################################

def get_sql_messages_by_sub_key(session, cluster_id, sub_key, last_sql_run, now, _initialized=_initialized):
    """ Returns all SQL messages queued up for a given sub_key that are not being delivered
    or have not been delivered already.
    """
    query = session.query(
        PubSubMessage.pub_msg_id,
        PubSubMessage.pub_correl_id,
        PubSubMessage.in_reply_to,
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
        PubSubMessage.has_gd,
    ).\
    filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
    filter(PubSubEndpointEnqueuedMessage.subscription_id==PubSubSubscription.id).\
    filter(PubSubEndpointEnqueuedMessage.delivery_status==_initialized).\
    filter(PubSubSubscription.sub_key==sub_key).\
    filter(PubSubMessage.expiration_time > now).\
    filter(PubSubMessage.cluster_id==cluster_id)

    if last_sql_run:
        query = query.\
            filter(PubSubMessage.pub_time > last_sql_run)

    query = query.\
        order_by(PubSubMessage.priority.desc()).\
        order_by(PubSubMessage.ext_pub_time).\
        order_by(PubSubMessage.pub_time)

    return query.all()

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
        where(PubSubEndpointEnqueuedMessage.subscription_id==PubSubSubscription.id).\
        where(PubSubSubscription.sub_key==sub_key)
    )

# ################################################################################################################################

def get_delivery_server_for_sub_key(session, cluster_id, sub_key, is_wsx):
    """ Returns information about which server handles delivery tasks for input sub_key, the latter must exist in DB.
    Assumes that sub_key belongs to a non-WSX endpoint and then checks WebSockets in case the former query founds
    no matching server.
    """
    # Sub key belongs to a WebSockets client ..
    if is_wsx:
        return Bunch({
            'server_id': 1,
            'server_name': 'server1',
            'cluster_id': 1,
            'endpoint_type': _wsx
        })
        return session.query(
            Server.id.label('server_id'),
            Server.name.label('server_name'),
            Server.cluster_id,
            expr.bindparam('endpoint_type', _wsx),
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
