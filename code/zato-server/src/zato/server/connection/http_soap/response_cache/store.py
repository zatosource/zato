# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha256
from http.client import MULTIPLE_CHOICES, NOT_MODIFIED, OK
from time import time

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.exception import HTTP_RESPONSES
from zato.server.connection.http_soap.response_cache.common import ModuleCtx
from zato.server.metrics import zato_rest_channel_cache_operations_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strnone
    from zato.server.connection.cache import CacheAPI
    from zato.server.connection.http_soap.response_cache.common import ResponseCacheContext
    CacheAPI = CacheAPI
    ResponseCacheContext = ResponseCacheContext

# ################################################################################################################################
# ################################################################################################################################

_response_cache = HTTP_SOAP.ResponseCache

# HTTP status lines, e.g. 200 -> '200 OK'
_status_response = {}
for _code, _reason in HTTP_RESPONSES.items():
    _status_response[_code] = f'{_code} {_reason}'

# The boundaries of the 200-class of status codes - the only class the cache stores
_min_ok_status = OK
_max_ok_status = MULTIPLE_CHOICES

# ################################################################################################################################
# ################################################################################################################################

def serve_hit(ctx:'ResponseCacheContext', entry:'stranydict', outcome:'str') -> 'str':
    """ Turns a stored entry into the response of the current request, setting the cache headers
    and short-circuiting to a bodyless 304 when the caller's ETag still matches.
    """
    headers = ctx.wsgi_environ['zato.http.response.headers']
    headers[ModuleCtx.Header_Cache] = ModuleCtx.Cache_Hit

    # The Age header carries how long ago the entry was stored, in whole seconds
    age_seconds = int(time() - entry['stored_at'])
    headers[ModuleCtx.Header_Age] = str(age_seconds)

    if ctx.config.needs_etag:
        etag = entry['etag']
        headers[ModuleCtx.Header_ETag] = etag

        # A matching ETag means the caller already has this body
        if ctx.if_none_match:
            if ctx.if_none_match == etag:
                ctx.wsgi_environ['zato.http.response.status'] = _status_response[NOT_MODIFIED]
                zato_rest_channel_cache_operations_total.labels(
                    ctx.channel_name, ModuleCtx.Outcome_Not_Modified).inc()

                return ''

    headers['Content-Type'] = entry['content_type']
    ctx.wsgi_environ['zato.http.response.status'] = _status_response[entry['status_code']]

    zato_rest_channel_cache_operations_total.labels(ctx.channel_name, outcome).inc()

    out = entry['body']
    return out

# ################################################################################################################################

def lookup(ctx:'ResponseCacheContext') -> 'strnone':
    """ Returns the cached response of this request or None on a miss. A miss with an admission
    marker in place makes the key eligible for coalescing and a full store.
    """

    # A no-cache request never reads from the cache
    if ctx.skip_lookup:
        zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Bypass).inc()
        return None

    value = ctx.cache_api.get(ctx.key)

    # Nothing under the key at all - a first-ever miss
    if value is None:
        zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Miss).inc()
        return None

    # The admission marker - a miss, but the key has proven it repeats
    if value == ModuleCtx.Marker:
        ctx.is_admitted = True
        zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Miss).inc()
        return None

    # A full entry - serve it as is
    ctx.is_admitted = True

    out = serve_hit(ctx, value, ModuleCtx.Outcome_Hit)
    return out

# ################################################################################################################################

def store(ctx:'ResponseCacheContext', body:'any_', status_code:'int') -> 'None':
    """ Stores a fresh response under the request's key, subject to the storage rules -
    only 200-class responses, never ones carrying Set-Cookie, size-capped, and behind
    the admission marker when cache-on-second-request is on.
    """
    headers = ctx.wsgi_environ['zato.http.response.headers']

    # The response goes out uncached no matter what happens below
    headers[ModuleCtx.Header_Cache] = ModuleCtx.Cache_Miss

    # Only textual bodies are stored - the wire always carries text on REST and SOAP channels
    if isinstance(body, bytes):
        try:
            body = body.decode('utf8')
        except UnicodeDecodeError:
            return

    if not isinstance(body, str):
        return

    # Only 200-class responses are cacheable ..
    if not (_min_ok_status <= status_code < _max_ok_status):
        return

    # .. responses that set cookies are never shared through the cache ..
    for header_name in headers:
        if header_name.lower() == 'set-cookie':
            return

    # .. and responses above the size cap bypass caching entirely.
    if len(body) > ctx.config.max_body_size:
        zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Bypass).inc()
        return

    # The first miss of a key stores a one-byte marker instead of the body - one-hit-wonder
    # keys then cost one expiring marker, not a dead body.
    if ctx.config.cache_on_second_request:
        if not ctx.is_admitted:
            ctx.cache_api.set(ctx.key, ModuleCtx.Marker, ctx.config.ttl_seconds)
            zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Marker_Stored).inc()
            return

    if ctx.config.needs_etag:
        etag = sha256(body.encode('utf8')).hexdigest()
    else:
        etag = ''

    entry = {
        'body': body,
        'content_type': headers['Content-Type'],
        'status_code': status_code,
        'stored_at': time(),
        'etag': etag,
        'path': ctx.path_and_query,
    }

    ctx.cache_api.set(ctx.key, entry, ctx.config.ttl_seconds)
    zato_rest_channel_cache_operations_total.labels(ctx.channel_name, ModuleCtx.Outcome_Stored).inc()

# ################################################################################################################################

def purge_channel(cache_api:'CacheAPI', channel_id:'int') -> 'None':
    """ Deletes all the cached responses of one channel - a prefix delete over its key space.
    """
    prefix = _response_cache.Key_Prefix.format(channel_id)
    cache_api.delete_by_prefix(prefix)

# ################################################################################################################################
# ################################################################################################################################
