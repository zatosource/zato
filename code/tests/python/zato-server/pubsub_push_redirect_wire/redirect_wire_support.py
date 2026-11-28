# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What the tests of the follow loop deliver with - a message of a subscription, the outgoing REST connection
# of its endpoint as the config store holds it, and the responses that redirect a push.

# stdlib
from http.client import TEMPORARY_REDIRECT
from weakref import finalize

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.payload_cache import PayloadCache, PayloadEpoch
from zato.common.typing_ import cast_
from zato.server.base.parallel.delivery_rest import deliver_to_rest, Push_Timeout
from zato.server.base.parallel.push_engine_client import PushEngineClient

# Test support
from http_endpoint.endpoint import EndpointResponse
from rest_outgoing_stub.connection import new_connection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from rest_outgoing_stub.connection import ServerStub
    from zato.common.typing_ import any_, anydict
    from zato.server.config import ConfigStore
    from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper
    ConfigStore = ConfigStore

# ################################################################################################################################
# ################################################################################################################################

# The subscription that each message is delivered for
Sub_Key = 'zpsk.rest.redirect.orders'

# The ID of the outgoing REST connection of the endpoint of the subscription
Endpoint_ID = 1

# The headers of a push that each hop receives unchanged
Push_Headers = ('Content-Type', 'X-Zato-Msg-ID', 'X-Zato-Delivery-Attempt')

# The headers that no hop receives
Absent_Headers = ('Authorization', 'Cookie')

# The topic that each message is published to
_topic_name = 'test.redirect.orders'

# The time of publication of each message
_pub_time_iso = '2026-11-23T21:00:00.000000+00:00'

# The text that each payload repeats
_payload_filler = 'Order 12345 for John Smith, two items, shipped to 120 Main Street. '

# How many bytes of escaped payloads the cache of each delivery keeps
_payload_cache_size = 64 * 1024 * 1024

# How many hex characters the random part of a message ID has
_msg_id_bits = 32

# The threads of the push engine of each delivery, one, so that its pushes reuse one keep-alive connection in order
_engine_threads = 1

# How many idle connections the push engine of each delivery keeps per endpoint
_engine_pool_size = 2

# ################################################################################################################################
# ################################################################################################################################

def new_payload(size:'int') -> 'str':
    """ Returns a payload of exactly the given number of characters.
    """
    filler_length = len(_payload_filler)
    repeat_count = size // filler_length + 1

    out = _payload_filler * repeat_count
    out = out[:size]

    return out

# ################################################################################################################################

def new_message(payload:'str', delivery_attempt:'int'=1) -> 'anydict':
    """ Returns a message as the delivery of a subscription receives it.
    """
    suffix = CryptoManager.generate_hex_string(_msg_id_bits)

    out:'anydict' = {
        'delivery_id': 1,
        'msg_id': f'zpsm.{suffix}',
        'delivery_attempt': delivery_attempt,
        'topic_name': _topic_name,
        'pub_time_iso': _pub_time_iso,
        'data': payload,
    }

    return out

# ################################################################################################################################

def redirect_to(location:'str', status:'int'=TEMPORARY_REDIRECT, **kwargs:'any_') -> 'EndpointResponse':
    """ Returns a response that redirects a push to the location with the status.
    """
    headers = [('Location', location)]

    out = EndpointResponse(status, headers=headers, **kwargs)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _OutconnItem:
    """ An outgoing REST connection as the config store holds it, with its address and its connection.
    """

    def __init__(self, base:'str', path:'str', conn:'HTTPSOAPWrapper') -> 'None':
        self.config = {'host': base, 'url_path': path}
        self.conn = conn

# ################################################################################################################################

class _OutconnStore:
    """ The outgoing REST connections of the config store, which hold the connection of the subscription.
    """

    def __init__(self, item:'_OutconnItem') -> 'None':
        self._item = item

    def get_by_id(self, endpoint_id:'int') -> '_OutconnItem | None':
        if endpoint_id == Endpoint_ID:
            out = self._item
        else:
            out = None

        return out

# ################################################################################################################################

class _ConfigStoreStub:
    """ The part of the config store that a delivery reads.
    """

    def __init__(self, item:'_OutconnItem') -> 'None':
        self.out_plain_http = _OutconnStore(item)

# ################################################################################################################################
# ################################################################################################################################

class Delivery:
    """ The deliveries of a subscription whose endpoint is at the base and the path, through one outgoing connection
    and one push engine, so that consecutive pushes share the pool of connections of the engine.
    """

    def __init__(self, server:'ServerStub', base:'str', path:'str', **kwargs:'any_') -> 'None':
        self.connection = new_connection(server, base, path, **kwargs)

        item = _OutconnItem(base, path, self.connection)
        self.config_store = _ConfigStoreStub(item)

        epoch = PayloadEpoch()
        self.payload_cache = PayloadCache(_payload_cache_size, epoch)

        # The engine stops, and its threads exit, once the delivery is no longer referenced
        self.engine = PushEngineClient(_engine_threads, _engine_pool_size, Push_Timeout)
        _ = finalize(self, self.engine.stop)

        self.sub_config:'anydict' = {
            'sub_key': Sub_Key,
            'rest_push_endpoint_id': Endpoint_ID,
        }

# ################################################################################################################################

    def push(self, message:'anydict') -> 'None':
        """ Delivers one attempt of the message, raising if the attempt fails.
        """
        config_store = cast_('ConfigStore', self.config_store)
        deliver_to_rest(self.engine, config_store, self.payload_cache, message, self.sub_config)

# ################################################################################################################################
# ################################################################################################################################
