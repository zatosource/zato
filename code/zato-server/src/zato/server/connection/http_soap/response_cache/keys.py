# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha256
from urllib.parse import parse_qsl

# Zato
from zato.common.api import HTTP_SOAP
from zato.server.connection.http_soap.response_cache.common import ModuleCtx, ResponseCacheContext
from zato.server.connection.http_soap.response_cache.config import get_channel_config
from zato.server.metrics import zato_rest_channel_cache_operations_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple, stranydict, strlist
    from zato.server.connection.cache import CacheAPI
    from zato.server.connection.http_soap.response_cache.common import ResponseCacheConfig
    anydict = anydict
    CacheAPI = CacheAPI
    ResponseCacheConfig = ResponseCacheConfig

# ################################################################################################################################
# ################################################################################################################################

_response_cache = HTTP_SOAP.ResponseCache

# ################################################################################################################################
# ################################################################################################################################

def _build_key_material(
    config:'ResponseCacheConfig',
    channel_id:'int',
    wsgi_environ:'stranydict',
    payload:'bytes',
    ) -> 'anytuple':
    """ Assembles the composite string the cache key is hashed from, along with the human-readable
    path and query stored inside entries for pattern-based invalidation.
    """

    # The HTTP method and the matched path vary the key for free ..
    method = wsgi_environ['REQUEST_METHOD']
    path = wsgi_environ['PATH_INFO']

    # .. the query string is sorted by parameter name with the opted-out names stripped,
    # so parameter order never splits the cache and tracking junk never varies it ..
    query_string = wsgi_environ.get('QUERY_STRING')

    if query_string is None:
        query_string = ''

    query_parameters = parse_qsl(query_string)
    kept_parameters:'strlist' = []

    for name, value in query_parameters:
        if name not in config.ignored_query_parameters:
            kept_parameters.append(f'{name}={value}')

    kept_parameters.sort()
    sorted_query = '&'.join(kept_parameters)

    # .. the caller's security definition name joins the key unless the channel explicitly
    # shares responses across callers - no response can leak between consumers by omission ..
    if config.is_shared_across_callers:
        caller = ''
    else:
        if sec_def_info := wsgi_environ.get('zato.sec_def'):
            caller = sec_def_info['name']
        else:
            caller = ''

    # .. values of the opted-in headers join the key too ..
    vary_values:'strlist' = []

    for header_name in config.vary_by_headers:
        wsgi_key = 'HTTP_' + header_name.upper().replace('-', '_')
        header_value = wsgi_environ.get(wsgi_key)

        if header_value is None:
            header_value = ''

        vary_values.append(header_value)

    vary_part = '\n'.join(vary_values)

    # .. and the body hash when the body is part of the key.
    if config.include_body_in_key:
        body_hash = sha256(payload).hexdigest()
    else:
        body_hash = ''

    material = '\n'.join((str(channel_id), method, path, sorted_query, caller, vary_part, body_hash))

    if sorted_query:
        path_and_query = f'{path}?{sorted_query}'
    else:
        path_and_query = path

    out = (material, path_and_query)
    return out

# ################################################################################################################################

def get_context(
    cache_api:'CacheAPI',
    channel_item:'anydict',
    wsgi_environ:'stranydict',
    payload:'bytes',
    ) -> 'ResponseCacheContext | None':
    """ Returns the response cache context of one request, or None when caching does not apply -
    because the channel has no enabled config, the method is not cacheable, or the request body
    exceeds the configured size cap.
    """
    config = get_channel_config(channel_item)

    if not config:
        return None

    if not config.is_enabled:
        return None

    channel_name = channel_item['name']

    # GET and HEAD are cacheable as they are, POST only when the body joins the key ..
    method = wsgi_environ['REQUEST_METHOD']

    if method not in ModuleCtx.Safe_Methods:
        if method != ModuleCtx.Body_Method:
            return None
        if not config.include_body_in_key:
            return None

    # .. a request body above the cap bypasses caching entirely ..
    if config.include_body_in_key:
        if len(payload) > config.max_body_size:
            zato_rest_channel_cache_operations_total.labels(channel_name, ModuleCtx.Outcome_Bypass).inc()
            return None

    channel_id = channel_item['id']
    material, path_and_query = _build_key_material(config, channel_id, wsgi_environ, payload)

    material_hash = sha256(material.encode('utf8')).hexdigest()
    key_prefix = _response_cache.Key_Prefix.format(channel_id)

    out = ResponseCacheContext()
    out.cache_api = cache_api
    out.config = config
    out.channel_id = channel_id
    out.channel_name = channel_name
    out.key = key_prefix + material_hash
    out.path_and_query = path_and_query
    out.wsgi_environ = wsgi_environ

    # Whether the key has an admission marker or a full entry is only known after the lookup
    out.is_admitted = False

    # A no-cache request skips the lookup but still stores the fresh response -
    # standard refresh semantics, the only client-controlled behavior supported.
    cache_control = wsgi_environ.get('HTTP_CACHE_CONTROL')

    if cache_control is None:
        cache_control = ''

    out.skip_lookup = 'no-cache' in cache_control

    if_none_match = wsgi_environ.get('HTTP_IF_NONE_MATCH')

    if if_none_match is None:
        if_none_match = ''

    out.if_none_match = if_none_match

    return out

# ################################################################################################################################
# ################################################################################################################################
