# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# requests
from requests import post as requests_post

# Zato
from zato.common.api import MISC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    from zato.server.config import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

# How long one push to a REST endpoint may take, in seconds, the same as for an outgoing REST connection,
# so that an endpoint that never responds fails the attempt rather than holding up the queue.
_rest_push_timeout = MISC.DEFAULT_HTTP_TIMEOUT

# The headers of a push request that identify the message and its attempt
_header_msg_id = 'X-Zato-Msg-ID'
_header_delivery_attempt = 'X-Zato-Delivery-Attempt'

# The header of a push response that declares the length of its body, absent from a chunked response
_header_content_length = 'Content-Length'

# ################################################################################################################################
# ################################################################################################################################

def get_rest_push_url(config_store:'ConfigStore', sub_config:'anydict') -> 'str':
    """ Returns the address of the outgoing REST connection that a subscription pushes to, as the connection holds it
    at the time of the delivery, so that a change of its host or path applies to the next delivery.
    """
    endpoint_id = sub_config['rest_push_endpoint_id']
    outconn = config_store.out_plain_http.get_by_id(endpoint_id)

    # A connection deleted while its subscription remains fails the attempt, which the retry policy repeats
    if outconn is None:
        raise Exception(f'No outgoing REST connection with ID {endpoint_id} for sub_key `{sub_config["sub_key"]}`')

    config = outconn.config

    # The host column is nullable in the ODB
    host = config['host']
    if host is None:
        host = ''

    out = host + config['url_path']
    return out

# ################################################################################################################################

def deliver_to_rest(config_store:'ConfigStore', message:'anydict', sub_config:'anydict') -> 'None':
    """ Delivers a raw message by posting it to the REST endpoint of its subscription.
    """
    url = get_rest_push_url(config_store, sub_config)

    # Each copy of a message carries its identifier and the number of its attempt, in the body and in the headers,
    # by which a subscriber recognizes a copy it processed already. The delivery row is internal to the database.
    envelope = dict(message)
    del envelope['delivery_id']

    headers = {
        'Content-Type': 'application/json',
        _header_msg_id: message['msg_id'],
        _header_delivery_attempt: str(message['delivery_attempt']),
    }

    response = requests_post(url, data=dumps(envelope), headers=headers, timeout=_rest_push_timeout)
    response.raise_for_status()

    # A response that ends before the length it declared is a failed attempt - the endpoint closed the connection
    # in the middle of it, so it may not have processed the message. The bytes are counted as received, before decoding.
    content_length = response.headers.get(_header_content_length)

    if content_length is not None:
        expected = int(content_length)
        received = response.raw.tell()

        if received < expected:
            raise Exception(f'Incomplete response from {url}, received {received} of {expected} bytes')

# ################################################################################################################################
# ################################################################################################################################
