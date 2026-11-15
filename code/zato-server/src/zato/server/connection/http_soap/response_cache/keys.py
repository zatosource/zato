# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha256
from json import dumps
from urllib.parse import parse_qsl

# Zato
from zato.common.api import HTTP_SOAP
from zato.server.connection.http_soap.response_cache.common import ModuleCtx, parse_cache_control, ResponseCacheContext
from zato.server.connection.http_soap.response_cache.config import get_channel_config
from zato.server.metrics import zato_rest_channel_cache_operations_total

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anytuple, stranydict, strlist
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

def _is_plain_value(value:'any_') -> 'bool':
    """ Returns True when a value consists only of strings, numbers, booleans, None, lists and dicts with string keys,
    which serialize to the same text in every process.
    """
    if value is None:
        return True

    if isinstance(value, (str, int, float, bool)):
        return True

    if isinstance(value, (list, tuple)):
        for item in value:
            if not _is_plain_value(item):
                return False
        return True

    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if not isinstance(item_key, str):
                return False
            if not _is_plain_value(item_value):
                return False
        return True

    return False

# ################################################################################################################################

def get_channel_fingerprint(channel_item:'anydict') -> 'str':
    """ Returns the fingerprint of the configuration of a channel item, the hash of its plain values, which is the same
    in every process that built the item from the same configuration. The fingerprint is memoized on the channel item -
    a configuration change rebuilds the item, which drops the memoized value along with it.
    """

    # The memoized value may exist from a previous request ..
    if ModuleCtx.Fingerprint_Key in channel_item:
        out = channel_item[ModuleCtx.Fingerprint_Key]
        return out

    # .. otherwise, the plain values are collected, without the ones that requests memoize on the item,
    # and without objects whose representation differs between processes ..
    plain:'stranydict' = {}

    for name, value in channel_item.items():
        if name in ModuleCtx.Fingerprint_Excluded_Keys:
            continue
        if _is_plain_value(value):
            plain[name] = value

    # .. and their canonical serialization is hashed and memoized.
    serialized = dumps(plain, sort_keys=True)
    out = sha256(serialized.encode('utf8')).hexdigest()

    channel_item[ModuleCtx.Fingerprint_Key] = out

    return out

# ################################################################################################################################

def _build_key_material(
    config:'ResponseCacheConfig',
    channel_id:'int',
    fingerprint:'str',
    request_ctx:'stranydict',
    payload:'bytes',
    ) -> 'anytuple':
    """ Assembles the composite string the cache key is hashed from, along with the human-readable
    path and query stored inside entries for pattern-based invalidation.
    """

    # The HTTP method and the matched path vary the key for free ..
    method = request_ctx['REQUEST_METHOD']
    path = request_ctx['PATH_INFO']

    # .. the query string is sorted by parameter name with the opted-out names stripped,
    # so parameter order never splits the cache and tracking junk never varies it ..
    query_string = request_ctx.get('QUERY_STRING')

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
    # shares responses across callers - no response can cross between consumers by omission ..
    if config.is_shared_across_callers:
        caller = ''
    else:
        if sec_def_info := request_ctx.get('zato.sec_def'):
            caller = sec_def_info['name']
        else:
            caller = ''

    # .. values of the opted-in headers join the key too ..
    vary_values:'strlist' = []

    for header_name in config.vary_by_headers:
        header_key = 'HTTP_' + header_name.upper().replace('-', '_')
        header_value = request_ctx.get(header_key)

        if header_value is None:
            header_value = ''

        vary_values.append(header_value)

    vary_part = '\n'.join(vary_values)

    # .. and the body hash when the body is part of the key.
    if config.include_body_in_key:
        body_hash = sha256(payload).hexdigest()
    else:
        body_hash = ''

    material = '\n'.join((str(channel_id), fingerprint, method, path, sorted_query, caller, vary_part, body_hash))

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
    request_ctx:'stranydict',
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

    # Requests carrying cookies are cached only when the channel varies its entries by the Cookie header ..
    if ModuleCtx.Cookie_Header in request_ctx:
        if ModuleCtx.Cookie_Header_Name not in config.vary_by_headers:
            zato_rest_channel_cache_operations_total.labels(channel_name, ModuleCtx.Outcome_Not_Cached).inc()
            return None

    # .. GET and HEAD are cacheable as they are, POST only when the body joins the key ..
    method = request_ctx['REQUEST_METHOD']

    if method not in ModuleCtx.Safe_Methods:
        if method != ModuleCtx.Body_Method:
            return None
        if not config.include_body_in_key:
            return None

    # .. a request body above the cap is not cached ..
    if config.include_body_in_key:
        if len(payload) > config.max_body_size:
            zato_rest_channel_cache_operations_total.labels(channel_name, ModuleCtx.Outcome_Not_Cached).inc()
            return None

    channel_id = channel_item['id']

    # A response computed under one configuration of the channel is stored under a key that no request
    # dispatched under another configuration reads
    fingerprint = get_channel_fingerprint(channel_item)

    material, path_and_query = _build_key_material(config, channel_id, fingerprint, request_ctx, payload)

    material_hash = sha256(material.encode('utf8')).hexdigest()
    key_prefix = _response_cache.Key_Prefix.format(channel_id)

    out = ResponseCacheContext()
    out.cache_api = cache_api
    out.config = config
    out.channel_id = channel_id
    out.channel_name = channel_name
    out.key = key_prefix + material_hash
    out.path_and_query = path_and_query
    out.request_ctx = request_ctx

    # Whether the key has an admission marker or a full entry is only known after the lookup
    out.is_admitted = False

    # A no-cache request skips the lookup but still stores the fresh response -
    # standard refresh semantics, the only client-controlled behavior supported.
    cache_control = request_ctx.get('HTTP_CACHE_CONTROL')

    if cache_control is None:
        cache_control = ''

    directives = parse_cache_control(cache_control)
    out.skip_lookup = ModuleCtx.Directive_No_Cache in directives

    if_none_match = request_ctx.get('HTTP_IF_NONE_MATCH')

    if if_none_match is None:
        if_none_match = ''

    out.if_none_match = if_none_match

    return out

# ################################################################################################################################
# ################################################################################################################################
