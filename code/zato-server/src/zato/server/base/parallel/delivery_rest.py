# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import PERMANENT_REDIRECT, TEMPORARY_REDIRECT
from json import loads
from logging import getLogger
from urllib.parse import urljoin, urlsplit, urlunsplit

# requests
from requests.exceptions import HTTPError

# Zato - Rust
from zato_common_core.zato_common_core import encode_push_envelope_parts

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.payload_cache import PayloadCache
    from zato.common.typing_ import any_, anydict, anylist, bytestuple, strnone, strset
    from zato.server.config import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many redirects one attempt of a push follows
Max_Push_Redirects = 5

# The statuses of a redirect that keeps the method and the body of the request
_redirect_statuses = {TEMPORARY_REDIRECT, PERMANENT_REDIRECT}

# The schemes of an address a push is redirected to
_scheme_http = 'http'
_scheme_https = 'https'
_redirect_schemes = {_scheme_http, _scheme_https}

# The network scopes of the first push of an attempt under which its redirects are followed
_redirect_scopes = {'public', 'private', 'loopback'}

# The header of a redirect that names its target, by the lowercase name the transport stores it under
_header_location = 'location'

# The range of the characters of a Location value, which excludes whitespace, control characters and non-ASCII characters
_location_char_min = 0x21
_location_char_max = 0x7e

# The lowest port of an address
_port_min = 1

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

# The header of a push response that declares the length of its body, absent from a chunked response,
# by the lowercase name the transport stores it under
_header_content_length = 'content-length'

# The ranges of the status codes of a success, of client errors and of server errors
_success_min = 200
_success_max = 300
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

def _check_location(location:'str') -> 'None':
    """ Raises for a Location value that contains whitespace, control characters or characters outside ASCII.
    """
    if not location:
        raise PushRedirectError('Redirect with an empty Location header')

    for char in location:
        code = ord(char)

        if code < _location_char_min:
            raise PushRedirectError(f'Redirect to {location!r} with a character outside of the range of a Location')

        if code > _location_char_max:
            raise PushRedirectError(f'Redirect to {location!r} with a character outside of the range of a Location')

# ################################################################################################################################

def _resolve_location(url:'str', location:'str') -> 'str':
    """ Resolves a Location value against the current address and returns the next address, without a fragment,
    raising for an address that is not a valid address of an HTTP or HTTPS endpoint.
    """
    resolved = urljoin(url, location)
    parts = urlsplit(resolved)

    # A scheme in upper case is accepted and lowercased ..
    scheme = parts.scheme.lower()

    if scheme not in _redirect_schemes:
        raise PushRedirectError(f'Redirect to `{location}` with a scheme other than http and https')

    # .. user information is not accepted ..
    if '@' in parts.netloc:
        raise PushRedirectError(f'Redirect to `{location}` with user information')

    # .. a host is required ..
    if not parts.hostname:
        raise PushRedirectError(f'Redirect to `{location}` without a host')

    # .. and so is a valid port, if one is given.
    try:
        port = parts.port
    except ValueError:
        raise PushRedirectError(f'Redirect to `{location}` with an invalid port')

    if port is not None:
        if port < _port_min:
            raise PushRedirectError(f'Redirect to `{location}` with an invalid port')

    out = urlunsplit((scheme, parts.netloc, parts.path, parts.query, ''))
    return out

# ################################################################################################################################

def get_push_redirect(
    url:'str',
    status_code:'int',
    header_store:'anydict',
    hop_count:'int',
    first_scope:'strnone',
    ) -> 'strnone':
    """ Returns the address that a response to a push redirects to, or None for a response that is not a redirect
    to be followed. Raises for a redirect that is not followed - a redirect beyond the limit, a redirect
    of a push whose first address has no network scope or is link-local, and a redirect to an address
    that is not valid, uses another scheme than HTTP or HTTPS, or uses HTTP after HTTPS.
    """
    # Only the statuses that keep the method and the body are followed ..
    if status_code not in _redirect_statuses:
        return None

    # .. within the network scope of the first push of the attempt ..
    if first_scope not in _redirect_scopes:
        raise PushRedirectError(f'Redirect {status_code} from `{url}` in the network scope `{first_scope}` is not followed')

    # .. up to a fixed number of times ..
    if hop_count >= Max_Push_Redirects:
        raise PushRedirectError(f'Redirect {status_code} from `{url}` beyond the limit of {Max_Push_Redirects} redirects')

    # .. to the address the redirect names ..
    if not (location := header_store.get(_header_location)):
        raise PushRedirectError(f'Redirect {status_code} from `{url}` without a Location header')

    location = location[1]
    _check_location(location)

    out = _resolve_location(url, location)

    # .. never using HTTP after HTTPS.
    current_scheme = urlsplit(url).scheme
    next_scheme = urlsplit(out).scheme

    if current_scheme == _scheme_https:
        if next_scheme == _scheme_http:
            raise PushRedirectError(f'Redirect {status_code} from `{url}` to `{out}` uses HTTP after HTTPS')

    return out

# ################################################################################################################################

def _raise_for_status(url:'str', status_code:'int', reason:'str') -> 'None':
    """ Raises for a response with any status code other than a success. A push is delivered only when its endpoint
    accepts it with a 2xx status, and a redirect that a push does not follow leaves the message undelivered.
    """
    if _success_min <= status_code < _success_max:
        return

    if _client_error_min <= status_code < _server_error_min:
        raise HTTPError(f'{status_code} Client Error: {reason} for url: {url}')

    if _server_error_min <= status_code < _server_error_max:
        raise HTTPError(f'{status_code} Server Error: {reason} for url: {url}')

    raise HTTPError(f'{status_code} Not a success: {reason} for url: {url}')

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

def _push_parts(
    outconn:'any_',
    url:'str',
    headers:'anydict',
    parts:'bytestuple',
    label:'str',
    sub_key:'str',
    ) -> 'tuple[str, bytes]':
    """ Posts the parts of a body to the address of a push, following its redirects, and returns the address
    that answered with the body of its response. Raises for a response that is not a complete success.
    """
    status_code, reason, header_store, response_body, _, _, first_scope = outconn.conn.invoke_pubsub_push(url, headers, parts)

    # Each redirect followed sends the same parts and headers to the next address, within the scope of the first push ..
    hop_count = 0

    while next_url := get_push_redirect(url, status_code, header_store, hop_count, first_scope):

        log_message = _redirect_messages[status_code]
        logger.info(log_message, label, sub_key, status_code, url, next_url)

        hop_count += 1
        url = next_url

        status_code, reason, header_store, response_body, _, _, _ = outconn.conn.invoke_pubsub_push(
            url, headers, parts, first_scope)

    # .. and the response of the last address decides the outcome of the attempt.
    _raise_for_status(url, status_code, reason)

    # A response that ends before the length it declared is a failed attempt - the endpoint closed the connection
    # in the middle of it, so it may not have processed the message. The bytes are counted as received, before decoding,
    # and each header is stored under its lowercase name as its original name and its value.
    if content_length := header_store.get(_header_content_length):
        expected = int(content_length[1])
        received = len(response_body)

        if received < expected:
            raise Exception(f'Incomplete response from {url}, received {received} of {expected} bytes')

    out = (url, response_body)
    return out

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

    # The identifier of the message and the number of its attempt are also in the headers
    headers = {
        'Content-Type': 'application/json',
        _header_msg_id: message['msg_id'],
        _header_delivery_attempt: str(message['delivery_attempt']),
    }

    parts = _get_envelope_parts(payload_cache, message)

    _ = _push_parts(outconn, url, headers, parts, message['msg_id'], sub_config['sub_key'])

# ################################################################################################################################

def parse_accepted_ids(url:'str', response_body:'bytes', msg_ids:'strset') -> 'strset':
    """ Returns the IDs that the response to a push of several messages accepted. A response that is not a JSON list
    of the strings of the IDs of the request accepts no message and is logged.
    """
    out:'strset' = set()

    try:
        accepted = loads(response_body)
    except ValueError:
        logger.warning('Push response from `%s` is not JSON, no message accepted', url)
        return out

    if not isinstance(accepted, list):
        logger.warning('Push response from `%s` is not a list, no message accepted', url)
        return out

    for msg_id in accepted:

        if not isinstance(msg_id, str):
            logger.warning('Push response from `%s` lists a value that is not a string, no message accepted', url)
            out.clear()
            return out

        if msg_id not in msg_ids:
            logger.warning('Push response from `%s` lists `%s`, not in the request, no message accepted', url, msg_id)
            out.clear()
            return out

        out.add(msg_id)

    return out

# ################################################################################################################################

def deliver_group_to_rest(
    config_store:'ConfigStore',
    payload_cache:'PayloadCache',
    messages:'anylist',
    sub_config:'anydict',
    ) -> 'strset':
    """ Delivers several messages in order by posting one JSON list of their envelopes to the REST endpoint
    of their subscription, and returns the IDs of the messages that the response accepted. Raises for a response
    that is not a complete success.
    """
    outconn = _get_rest_push_outconn(config_store, sub_config)
    url = _get_url(outconn)

    headers = {
        'Content-Type': 'application/json',
    }

    # The body is a JSON list of the envelopes, each written as its prefix, its escaped payload and its suffix ..
    parts:'list[bytes]' = [_list_start]
    msg_ids:'strset' = set()

    for idx, message in enumerate(messages):

        if idx:
            parts.append(_list_separator)

        parts.extend(_get_envelope_parts(payload_cache, message))
        msg_ids.add(message['msg_id'])

    parts.append(_list_end)

    # .. which goes out as one request ..
    label = f'{len(messages)} messages'
    url, response_body = _push_parts(outconn, url, headers, tuple(parts), label, sub_config['sub_key'])

    # .. whose response names the messages it accepted.
    out = parse_accepted_ids(url, response_body, msg_ids)
    return out

# ################################################################################################################################
# ################################################################################################################################
