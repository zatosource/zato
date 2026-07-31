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
    from zato.common.typing_ import any_, anytuple, callable_, strcalldict, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_topic_prefix   = PubSub.Outgoing.Topic_Prefix
_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

# The keys of the envelope that travels from a publisher to a delivery handler.
_key_conn_type = 'conn_type'
_key_conn_id   = 'conn_id'
_key_conn_name = 'conn_name'
_key_data      = 'data'

# Handlers that know how to hand a message over to a connection, keyed by connection type.
delivery_handlers:'strcalldict' = {}

# Functions that find one connection by the id it is published to under, keyed by connection type.
# Each of them answers with the connection's current name and the wrapper to hand a message to.
conn_locators:'strcalldict' = {}

# ################################################################################################################################
# ################################################################################################################################

def get_outgoing_topic_name(conn_type:'str', conn_name:'str') -> 'str':
    """ The name of the topic that carries messages destined for one outgoing connection. A rename
    of that connection moves the topic, which is the only thing about a queue that a name decides.
    """
    out = f'{_topic_prefix}{conn_type}.{conn_name}'
    out = out.lower()

    validate_topic_name(out)

    return out

# ################################################################################################################################

def get_outgoing_sub_key(conn_type:'str', conn_id:'int') -> 'str':
    """ The key of the queue in front of one outgoing connection. It is built from the connection's id
    rather than its name, so that a connection has the one queue for as long as it exists.
    """
    out = f'{_sub_key_prefix}{conn_type}.{conn_id}'
    return out

# ################################################################################################################################

def parse_outgoing_sub_key(sub_key:'str') -> 'anytuple':
    """ Turns a sub key back into the connection type and connection id it was built from.
    """
    remainder = sub_key[len(_sub_key_prefix):]
    conn_type, _, conn_id = remainder.rpartition('.')

    out = (conn_type, int(conn_id))
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

def register_outgoing_conn_type(conn_type:'str', locator:'callable_', handler:'callable_') -> 'None':
    """ Makes connections of one type publishable to. The locator answers with a connection's current
    name and its wrapper, the handler is what hands a message over to that wrapper.
    """
    conn_locators[conn_type] = locator
    delivery_handlers[conn_type] = handler

# ################################################################################################################################

def find_outgoing_conn(server:'ParallelServer', conn_type:'str', conn_id:'int') -> 'anytuple':
    """ Looks one outgoing connection up by its id, answering with the name it goes by now and its wrapper,
    or with nothing at all if there is no such connection, e.g. because it has been deleted since.
    """
    locator = conn_locators.get(conn_type)

    # A type that was never registered cannot be published to at all
    if not locator:
        raise Exception(f'No locator for outgoing connection type `{conn_type}`')

    out = locator(server, conn_id)
    return out

# ################################################################################################################################

def locate_outgoing_conn(server:'ParallelServer', conn_type:'str', conn_id:'int', conn_name:'str'='') -> 'anytuple':
    """ Finds one outgoing connection by its id, answering with the name it goes by now and its wrapper.
    The name a caller already has is used in errors only, because it may be the one from before a rename.
    """
    out = find_outgoing_conn(server, conn_type, conn_id)

    # A connection that is no longer there cannot be delivered to
    if not out:
        raise Exception(f'No outgoing {conn_type} connection with id `{conn_id}` (`{conn_name}`)')

    return out

# ################################################################################################################################

def deliver_envelope(server:'ParallelServer', cid:'str', envelope:'stranydict') -> 'None':
    """ Hands one published message over to the outgoing connection it was addressed to.
    Whatever is raised here is what makes the pub/sub delivery loop retry the message.
    """
    conn_type = envelope[_key_conn_type]
    conn_id = envelope[_key_conn_id]
    conn_name = envelope[_key_conn_name]
    data = envelope[_key_data]

    # The connection is looked up by id, so a message queued before a rename reaches the connection after it ..
    _, wrapper = locate_outgoing_conn(server, conn_type, conn_id, conn_name)

    # .. and the type's own handler is what knows how to give a message to that wrapper.
    handler = delivery_handlers[conn_type]
    handler(server, cid, wrapper, data)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingPublisher:
    """ Publishes messages to the topic in front of one outgoing connection.
    """

    def __init__(self, server:'ParallelServer', conn_type:'str', conn_id:'int') -> 'None':
        self.server = server
        self.conn_type = conn_type
        self.conn_id = conn_id

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return f'OutgoingPublisher({self.conn_type}/{self.conn_id} at {hex(id(self))})'

# ################################################################################################################################

    def publish(self, data:'any_'='', **kwargs:'any_') -> 'PublishResult':
        """ Queues one message for delivery to the connection, returning as soon as it is stored.
        """
        config_manager = self.server.config_manager

        # The connection's own lock is held for as long as it takes to find its topic and to write
        # to it, so that a rename of the connection either happens entirely before this publication
        # or entirely after it, never with the topic moving out from under a message being written.
        with config_manager.get_outgoing_publish_lock(self.conn_type, self.conn_id):

            # The topic and the queue in front of it are created on first use, and the topic follows
            # the connection's current name, which is why it is resolved here rather than once ..
            topic_name, conn_name = config_manager.ensure_outgoing_subscription(self.conn_type, self.conn_id)

            # .. handlers are given the payload as a string, so anything else is serialized here ..
            if not isinstance(data, str):
                data = dumps(data)

            # .. the envelope is what tells the delivery service which connection the message is for,
            # .. by id because that is what a rename leaves alone, with the name for what a log line says ..
            envelope = {
                _key_conn_type: self.conn_type,
                _key_conn_id: self.conn_id,
                _key_conn_name: conn_name,
                _key_data: data,
            }
            envelope = dumps(envelope)

            # .. and the message itself goes through the same backend as every other publication.
            out = self.server.pubsub_backend.publish(topic_name, envelope, **kwargs)

        return out

# ################################################################################################################################
# ################################################################################################################################
