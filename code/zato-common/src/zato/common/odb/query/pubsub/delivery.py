# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

# Zato
from zato.common.api import PUBSUB
from zato.common.odb.model import PubSubEndpoint, PubSubMessage, PubSubEndpointEnqueuedMessage, PubSubSubscription, Server, \
     WebSocketClient, WebSocketClientPubSubKeys
from zato.common.util.sql.retry import sql_op_with_deadlock_retry, sql_query_with_retry

# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_, anytuple, intnone, intset, listnone, strlist
    anytuple = anytuple
    intnone = intnone
    intset = intset
    listnone = listnone
    strlist = strlist
    SASession = SASession

# ################################################################################################################################

logger_zato = getLogger('zato')
logger_pubsub = getLogger('zato_pubsub')

# ################################################################################################################################

_initialized = PUBSUB.DELIVERY_STATUS.INITIALIZED
_delivered = PUBSUB.DELIVERY_STATUS.DELIVERED

_float_str=PUBSUB.FLOAT_STRING_CONVERT

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

def _get_base_sql_msg_query(
    session, # type: SASession
    columns, # type: anytuple
    sub_key_list, # type: strlist
    pub_time_max, # type: float
    cluster_id,   # type: int
    include_unexpired_only # type: bool
    ):
    query = session.query(*columns).\
        filter(PubSubEndpointEnqueuedMessage.pub_msg_id==PubSubMessage.pub_msg_id).\
        filter(PubSubEndpointEnqueuedMessage.sub_key.in_(sub_key_list)).\
        filter(PubSubEndpointEnqueuedMessage.delivery_status==_initialized)

    # If this flag is True, it means that we are returning only messages that have not expired yet.
    # It will be True when we use this query to deliver messages to subscribers as we want to deliver
    # only these messages that have not expired yet. However, during cleanup, when we delete all messages
    # that belong to a subscriber, this flag will be False because really need to delete them all,
    # regardless of whether they are already expired or not.
    if include_unexpired_only:
        query = query.\
            filter(PubSubMessage.expiration_time > _float_str.format(pub_time_max))

    if cluster_id:
        query = query.\
            filter(PubSubMessage.cluster_id==cluster_id)

    return query

# ################################################################################################################################

def _get_sql_msg_data_by_sub_key(
    session, # type: SASession
    cluster_id,   # type: int
    sub_key_list, # type: strlist
    last_sql_run, # type: float
    pub_time_max, # type: float
    columns,      # type: anytuple
    include_unexpired_only, # type: bool
    ignore_list=None, # type: listnone
    needs_result=True # type: bool
    ):
    """ Returns all SQL messages queued up for a given sub_key that are not being delivered
    or have not been delivered already.
    """
    logger_pubsub.info('Getting GD messages for `%s` last_run:%r pub_time_max:%r needs_result:%d unexp:%d', sub_key_list, last_sql_run,
        pub_time_max, int(needs_result), int(include_unexpired_only))

    query = _get_base_sql_msg_query(session, columns, sub_key_list, pub_time_max, cluster_id, include_unexpired_only)

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

    out = query.all() if needs_result else query
    return out

# ################################################################################################################################

def get_sql_messages_by_sub_key(
    session,      # type: SASession
    cluster_id,   # type: int
    sub_key_list, # type: strlist
    last_sql_run, # type: float
    pub_time_max, # type: float
    ignore_list,  # type: intset
    include_unexpired_only=True # type: bool
    ) -> 'any_':
    return _get_sql_msg_data_by_sub_key(session, cluster_id, sub_key_list, last_sql_run, pub_time_max,
        sql_messages_columns, include_unexpired_only, ignore_list)

# ################################################################################################################################

def get_sql_messages_by_msg_id_list(
    session,      # type: SASession
    cluster_id,   # type: int
    sub_key,      # type: str
    pub_time_max, # type: float
    msg_id_list,  # type: strlist
    include_unexpired_only=True # type: bool
    ) -> 'any_':
    query = _get_base_sql_msg_query(session, sql_messages_columns, [sub_key], pub_time_max, cluster_id, include_unexpired_only)
    return query.\
        filter(PubSubEndpointEnqueuedMessage.pub_msg_id.in_(msg_id_list))

# ################################################################################################################################

def get_sql_msg_ids_by_sub_key(
    session,      # type: SASession
    cluster_id,   # type: intnone
    sub_key,      # type: str
    last_sql_run, # type: float
    pub_time_max, # type: float
    include_unexpired_only=True, # type: bool
    needs_result=False           # type: bool
    ) -> 'any_':
    return _get_sql_msg_data_by_sub_key(session, cluster_id, [sub_key], last_sql_run, pub_time_max, sql_msg_id_columns,
        include_unexpired_only, needs_result=needs_result)

# ################################################################################################################################

def _confirm_pubsub_msg_delivered_query(
    session,    # type: SASession
    cluster_id, # type: int
    sub_key,    # type: str
    delivered_pub_msg_id_list, # type: strlist
    now                        # type: float
    ) -> 'None':
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

def _confirm_pubsub_msg_delivered(*args:'any_') -> 'bool':
    try:
        return sql_op_with_deadlock_retry(
            None,
            '_confirm_pubsub_msg_delivered_query',
            _confirm_pubsub_msg_delivered_query,
            *args
        )
    except IntegrityError:
        logger_zato.info('Caught IntegrityError (_confirm_pubsub_msg_delivered) `%s` -> `%s`', args, format_exc())
        return False

# ################################################################################################################################

def confirm_pubsub_msg_delivered(*args:'any_') -> 'None':
    sql_query_with_retry(_confirm_pubsub_msg_delivered, '_confirm_pubsub_msg_delivered', *args)

# ################################################################################################################################

def get_delivery_server_for_sub_key(
    session,    # type: SASession
    cluster_id, # type: int
    sub_key,    # type: str
    is_wsx      # type: bool
    ) -> 'any_':
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
