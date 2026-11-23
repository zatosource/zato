# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# requests
from requests.exceptions import HTTPError

# Zato - Rust
from zato_common_core.zato_common_core import encode_push_envelope_parts

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.payload_cache import PayloadCache
    from zato.common.typing_ import any_, anydict
    from zato.server.config import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

# The headers of a push request that identify the message and its attempt
_header_msg_id = 'X-Zato-Msg-ID'
_header_delivery_attempt = 'X-Zato-Delivery-Attempt'

# The key of a push envelope that holds the payload
_payload_key = 'data'

# The header of a push response that declares the length of its body, absent from a chunked response,
# by the lowercase name the transport stores it under
_header_content_length = 'content-length'

# The ranges of the status codes of client and server errors
_client_error_min = 400
_server_error_min = 500
_server_error_max = 600

# ################################################################################################################################
# ################################################################################################################################

def _get_rest_push_outconn(config_store:'ConfigStore', sub_config:'anydict') -> 'any_':
    """ Returns the outgoing REST connection that a subscription pushes to, as the config store holds it
    at the time of the delivery, so that a change of the connection applies to the next delivery.
    """
    endpoint_id = sub_config['rest_push_endpoint_id']
    out = config_store.out_plain_http.get_by_id(endpoint_id)

    # A connection deleted while its subscription remains fails the attempt, which the retry policy repeats
    if out is None:
        raise Exception(f'No outgoing REST connection with ID {endpoint_id} for sub_key `{sub_config["sub_key"]}`')

    return out

# ################################################################################################################################

def _get_url(outconn:'any_') -> 'str':
    """ Returns the address of an outgoing REST connection.
    """
    config = outconn.config

    # The host column is nullable in the ODB
    host = config['host']
    if host is None:
        host = ''

    out = host + config['url_path']
    return out

# ################################################################################################################################

def get_rest_push_url(config_store:'ConfigStore', sub_config:'anydict') -> 'str':
    """ Returns the address of the outgoing REST connection that a subscription pushes to.
    """
    outconn = _get_rest_push_outconn(config_store, sub_config)

    out = _get_url(outconn)
    return out

# ################################################################################################################################

def _raise_for_status(url:'str', status_code:'int', reason:'str') -> 'None':
    """ Raises the error requests raises for a response with a status code of a client or a server error.
    """
    if _client_error_min <= status_code < _server_error_min:
        raise HTTPError(f'{status_code} Client Error: {reason} for url: {url}')

    if _server_error_min <= status_code < _server_error_max:
        raise HTTPError(f'{status_code} Server Error: {reason} for url: {url}')

# ################################################################################################################################

def deliver_to_rest(
    config_store:'ConfigStore',
    payload_cache:'PayloadCache',
    message:'anydict',
    sub_config:'anydict',
    ) -> 'None':
    """ Delivers a raw message by posting it to the REST endpoint of its subscription,
    through the pub/sub transport of the outgoing REST connection of the endpoint.
    """
    outconn = _get_rest_push_outconn(config_store, sub_config)
    url = _get_url(outconn)

    # Each copy of a message carries its identifier and the number of its attempt, in the body and in the headers,
    # by which a subscriber recognizes a copy it processed already. The delivery row is internal to the database.
    envelope = dict(message)
    del envelope['delivery_id']

    headers = {
        'Content-Type': 'application/json',
        _header_msg_id: message['msg_id'],
        _header_delivery_attempt: str(message['delivery_attempt']),
    }

    # The body is the envelope around its payload. The envelope has the attempt of this push, so it is encoded
    # for each push, whereas the payload is escaped once and shared by every push of the message.
    prefix, suffix = encode_push_envelope_parts(envelope, _payload_key)
    escaped = payload_cache.get_escaped(message['msg_id'], message[_payload_key])
    parts = (prefix, escaped, suffix)

    status_code, reason, header_store, response_body, _, _ = outconn.conn.invoke_pubsub_push(url, headers, parts)

    _raise_for_status(url, status_code, reason)

    # A response that ends before the length it declared is a failed attempt - the endpoint closed the connection
    # in the middle of it, so it may not have processed the message. The bytes are counted as received, before decoding,
    # and each header is stored under its lowercase name as its original name and its value.
    if content_length := header_store.get(_header_content_length):
        expected = int(content_length[1])
        received = len(response_body)

        if received < expected:
            raise Exception(f'Incomplete response from {url}, received {received} of {expected} bytes')

# ################################################################################################################################
# ################################################################################################################################
