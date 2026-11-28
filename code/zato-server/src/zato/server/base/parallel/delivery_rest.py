# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import PERMANENT_REDIRECT, TEMPORARY_REDIRECT
from logging import getLogger

# requests
from requests.exceptions import ChunkedEncodingError, ConnectionError as RequestsConnectionError, ConnectTimeout, \
    HTTPError, InvalidURL, ReadTimeout, SSLError

# Zato
from zato.common.api import MISC

# Zato - Rust
from zato_common_core.zato_common_core import encode_push_envelope_parts
from zato_server_core.zato_server_core import Max_Push_Redirects as Max_Push_Redirects # How many redirects a push follows

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.payload_cache import PayloadCache
    from zato.common.typing_ import any_, anydict, anylist, anytuple, bytestuple, strlist, strset
    from zato.server.base.parallel.push_engine_client import PushEngineClient
    from zato.server.config import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long each connect and each read of a push may take, in seconds, so that an endpoint that never responds
# fails the attempt rather than holding up the queue of its subscriber.
Push_Timeout = MISC.DEFAULT_HTTP_TIMEOUT

# What is logged for each redirect followed
_redirect_message = 'Push of `%s` for `%s` redirected with %s from `%s` to `%s`'
_moved_message = _redirect_message + ', the endpoint of the subscription moved permanently'

_redirect_messages = {
    TEMPORARY_REDIRECT: _redirect_message,
    PERMANENT_REDIRECT: _moved_message,
}

# ################################################################################################################################
# ################################################################################################################################

class PushRedirectError(Exception):
    """ A redirect of a push that is not followed, which fails the attempt.
    """

class PushReplyError(Exception):
    """ A response to a push of several messages that is not a JSON list of the IDs of the request.
    """

# ################################################################################################################################
# ################################################################################################################################

# The headers of a push request that identify the message and its attempt
_header_msg_id = 'X-Zato-Msg-ID'
_header_delivery_attempt = 'X-Zato-Delivery-Attempt'

# The key of a push envelope that holds the payload
_payload_key = 'data'

# The bytes around and between the envelopes of a push of several messages
_list_start = b'['
_list_separator = b','
_list_end = b']'

# The exception each kind of error of the push engine is raised as
_error_classes:'dict[str, type[Exception]]' = {
    'address': InvalidURL,
    'tls_config': SSLError,
    'connect_timeout': ConnectTimeout,
    'read_timeout': ReadTimeout,
    'connection': RequestsConnectionError,
    'tls': SSLError,
    'chunked': ChunkedEncodingError,
    'scope_refused': RequestsConnectionError,
    'redirect': PushRedirectError,
    'status': HTTPError,
    'incomplete': Exception,
    'reply': PushReplyError,
}

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

def _get_envelope_parts(payload_cache:'PayloadCache', message:'anydict') -> 'bytestuple':
    """ Returns the parts of the envelope of one message, its payload escaped in the middle.
    """
    # Each copy of a message carries its identifier and the number of its attempt, by which a subscriber recognizes
    # a copy it processed already. The delivery row is internal to the database.
    envelope = dict(message)
    del envelope['delivery_id']

    # The envelope has the attempt of this push, so it is encoded for each push, whereas the payload
    # is escaped once and shared by every push of the message.
    prefix, suffix = encode_push_envelope_parts(envelope, _payload_key)
    escaped = payload_cache.get_escaped(message['msg_id'], message[_payload_key])

    out = (prefix, escaped, suffix)
    return out

# ################################################################################################################################

def _push(
    engine:'PushEngineClient',
    outconn:'any_',
    request:'anytuple',
    label:'str',
    sub_key:'str',
    ) -> 'strlist':
    """ Sends one request through the push engine, following its redirects, and returns the IDs of the messages
    that it concluded. Raises for a request that was not fully concluded, with the exception of the error that ended it.
    """
    panic, outcomes = engine.run([request], Push_Timeout, outconn.conn.get_push_tls())

    # A panic of the engine is a defect, reported with the job it ended
    if panic is not None:
        logger.error('Push of `%s` for `%s` ended by a panic of the push engine: %s', label, sub_key, panic)
        raise Exception(f'Push of `{label}` ended by a panic of the push engine: {panic}')

    url, _status, _reason, concluded, _elapsed_us, _first_scope, error_kind, error_message, redirects = outcomes[0]

    # Each redirect followed is logged, whatever the outcome of the request ..
    for redirect_status, from_url, to_url in redirects:
        log_message = _redirect_messages[redirect_status]
        logger.info(log_message, label, sub_key, redirect_status, from_url, to_url)

    # .. and an error of the request fails the attempt.
    if error_kind is not None:
        error_class = _error_classes[error_kind]
        raise error_class(error_message)

    logger.debug('Push of `%s` for `%s` concluded by `%s`', label, sub_key, url)
    return concluded

# ################################################################################################################################

def deliver_to_rest(
    engine:'PushEngineClient',
    config_store:'ConfigStore',
    payload_cache:'PayloadCache',
    message:'anydict',
    sub_config:'anydict',
    ) -> 'None':
    """ Delivers a raw message by posting it to the REST endpoint of its subscription, through the push engine.
    """
    outconn = _get_rest_push_outconn(config_store, sub_config)
    url = _get_url(outconn)

    # The identifier of the message and the number of its attempt are also in the headers
    headers = {
        'Content-Type': 'application/json',
        _header_msg_id: message['msg_id'],
        _header_delivery_attempt: str(message['delivery_attempt']),
    }

    parts = _get_envelope_parts(payload_cache, message)
    request = (url, headers, parts, [message['msg_id']], False)

    _ = _push(engine, outconn, request, message['msg_id'], sub_config['sub_key'])

# ################################################################################################################################

def deliver_group_to_rest(
    engine:'PushEngineClient',
    config_store:'ConfigStore',
    payload_cache:'PayloadCache',
    messages:'anylist',
    sub_config:'anydict',
    ) -> 'strset':
    """ Delivers several messages in order by posting one JSON list of their envelopes to the REST endpoint
    of their subscription, and returns the IDs of the messages that the response accepted. A response that is not
    a JSON list of the IDs of the request accepts no message and is logged. Raises for any other failure.
    """
    outconn = _get_rest_push_outconn(config_store, sub_config)
    url = _get_url(outconn)
    sub_key = sub_config['sub_key']

    headers = {
        'Content-Type': 'application/json',
    }

    # The body is a JSON list of the envelopes, each written as its prefix, its escaped payload and its suffix ..
    parts:'list[bytes]' = [_list_start]
    msg_ids:'strlist' = []

    for idx, message in enumerate(messages):

        if idx:
            parts.append(_list_separator)

        parts.extend(_get_envelope_parts(payload_cache, message))
        msg_ids.append(message['msg_id'])

    parts.append(_list_end)

    # .. which goes out as one request ..
    label = f'{len(messages)} messages'
    request = (url, headers, tuple(parts), msg_ids, True)

    # .. whose response names the messages it accepted.
    try:
        concluded = _push(engine, outconn, request, label, sub_key)
    except PushReplyError as e:
        logger.warning('Push response for `%s`, no message accepted: %s', sub_key, e)
        concluded = []

    out = set(concluded)
    return out

# ################################################################################################################################
# ################################################################################################################################
