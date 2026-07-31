# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from logging import getLogger

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.util import validate_topic_name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import any_, callable_, strcalldict, stranydict, strtuple
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_topic_prefix   = PubSub.Outgoing.Topic_Prefix
_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

# The keys of the envelope that travels from a publisher to a delivery handler.
_key_conn_type = 'conn_type'
_key_conn_name = 'conn_name'
_key_data      = 'data'

# Handlers that know how to hand a message over to a connection, keyed by connection type.
delivery_handlers:'strcalldict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_outgoing_topic_name(conn_type:'str', conn_name:'str') -> 'str':
    """ The name of the topic that carries messages destined for one outgoing connection.
    """
    out = f'{_topic_prefix}{conn_type}.{conn_name}'
    out = out.lower()

    validate_topic_name(out)

    return out

# ################################################################################################################################

def get_outgoing_sub_key(conn_type:'str', conn_name:'str') -> 'str':
    """ The key of the queue in front of one outgoing connection. The connection's name keeps its
    original case because this is what the name is recovered from when a server starts.
    """
    out = f'{_sub_key_prefix}{conn_type}.{conn_name}'
    return out

# ################################################################################################################################

def parse_outgoing_sub_key(sub_key:'str') -> 'strtuple':
    """ Turns a sub key back into the connection type and connection name it was built from.
    """
    remainder = sub_key[len(_sub_key_prefix):]
    conn_type, _, conn_name = remainder.partition('.')

    out = (conn_type, conn_name)
    return out

# ################################################################################################################################

def get_outgoing_sub_config(sub_key:'str', topic_name:'str') -> 'stranydict':
    """ The push subscription that puts one outgoing connection's queue in front of the delivery service.
    """
    out = {
        'sub_key': sub_key,
        'topic_name': topic_name,
        'push_type': PubSub.Push_Type.Service,
        'push_service_name': PubSub.Outgoing.Delivery_Service,
        'rest_push_endpoint_id': None,
    }

    return out

# ################################################################################################################################

def register_delivery_handler(conn_type:'str', handler:'callable_') -> 'None':
    """ Makes connections of one type publishable to.
    """
    delivery_handlers[conn_type] = handler

# ################################################################################################################################

def deliver_envelope(server:'ParallelServer', cid:'str', envelope:'stranydict') -> 'None':
    """ Hands one published message over to the outgoing connection it was addressed to.
    Whatever is raised here is what makes the pub/sub delivery loop retry the message.
    """
    conn_type = envelope[_key_conn_type]
    conn_name = envelope[_key_conn_name]
    data = envelope[_key_data]

    # A type that has a handler is delivered to through it ..
    if handler := delivery_handlers.get(conn_type):
        handler(server, cid, conn_name, data)

    # .. and a type without one cannot be delivered to at all.
    else:
        raise Exception(f'No delivery handler for outgoing connection type `{conn_type}`')

# ################################################################################################################################
# ################################################################################################################################

class OutgoingPublisher:
    """ Publishes messages to the topic in front of one outgoing connection.
    """

    def __init__(self, server:'ParallelServer', conn_type:'str', conn_name:'str') -> 'None':
        self.server = server
        self.conn_type = conn_type
        self.conn_name = conn_name

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return f'OutgoingPublisher({self.conn_type}/{self.conn_name} at {hex(id(self))})'

# ################################################################################################################################

    def publish(self, data:'any_'='', **kwargs:'any_') -> 'PublishResult':
        """ Queues one message for delivery to the connection, returning as soon as it is stored.
        """

        # The connection's topic and the queue in front of it are created on first use ..
        topic_name = self.server.config_manager.ensure_outgoing_subscription(self.conn_type, self.conn_name)

        # .. handlers are given the payload as a string, so anything else is serialized here ..
        if not isinstance(data, str):
            data = dumps(data)

        # .. the envelope is what tells the delivery service which connection the message is for ..
        envelope = {
            _key_conn_type: self.conn_type,
            _key_conn_name: self.conn_name,
            _key_data: data,
        }
        envelope = dumps(envelope)

        # .. and the message itself goes through the same backend as every other publication.
        out = self.server.pubsub_backend.publish(topic_name, envelope, **kwargs)

        return out

# ################################################################################################################################
# ################################################################################################################################
