# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HTTP_SOAP, URL_TYPE
from zato.server.connection.http_soap.response_cache.common import ResponseCacheConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_response_cache = HTTP_SOAP.ResponseCache

# How many seconds one unit of the configured TTL represents
_TTL_Multipliers = {
    _response_cache.TTLUnit.Seconds: 1,
    _response_cache.TTLUnit.Minutes: 60,
    _response_cache.TTLUnit.Hours:   3600,
}

# ################################################################################################################################
# ################################################################################################################################

def get_default_config() -> 'stranydict':
    """ Returns a new dict with every response caching field set to its default value.
    """
    out = _response_cache.get_default_config()
    return out

# ################################################################################################################################

def parse_config(raw:'stranydict', transport:'str') -> 'ResponseCacheConfig':
    """ Turns the raw response_cache dict from a channel's opaque attributes into a parsed config object,
    applying defaults for any field the dict does not carry.
    """
    config = get_default_config()
    config.update(raw)

    out = ResponseCacheConfig()
    out.is_enabled = bool(config['is_enabled'])

    # The TTL and its unit are stored separately and combined into seconds here
    ttl_unit = config['ttl_unit']

    if ttl_unit not in _TTL_Multipliers:
        raise Exception(f'Unknown response cache TTL unit: `{ttl_unit}`')

    out.ttl_seconds = int(config['ttl']) * _TTL_Multipliers[ttl_unit]

    out.is_shared_across_callers = bool(config['is_shared_across_callers'])
    out.vary_by_headers          = list(config['vary_by_headers'])
    out.ignored_query_parameters = list(config['ignored_query_parameters'])

    # SOAP operations live in the POST body, so method plus path identifies nothing there -
    # the body hash is always part of the key for SOAP channels.
    if transport == URL_TYPE.SOAP:
        out.include_body_in_key = True
    else:
        out.include_body_in_key = bool(config['include_body_in_key'])

    out.max_body_size           = int(config['max_body_size'])
    out.cache_on_second_request = bool(config['cache_on_second_request'])
    out.needs_etag              = bool(config['needs_etag'])
    out.coalesce_timeout        = int(config['coalesce_timeout'])

    return out

# ################################################################################################################################

def get_channel_config(channel_item:'anydict') -> 'ResponseCacheConfig | None':
    """ Returns the parsed response caching config of a channel, or None if the channel has none.
    The parsed object is memoized on the channel item - a configuration change rebuilds the item,
    which drops the memoized value along with it.
    """

    # The memoized value may exist from a previous request ..
    if 'response_cache_parsed' in channel_item:
        out = channel_item['response_cache_parsed']
        return out

    # .. otherwise, parse the raw dict if there is one ..
    if raw := channel_item.get('response_cache'):
        out = parse_config(raw, channel_item['transport'])
    else:
        out = None

    # .. and memoize the result, be it a config object or None.
    channel_item['response_cache_parsed'] = out

    return out

# ################################################################################################################################
# ################################################################################################################################
