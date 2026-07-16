# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist
    from zato.server.connection.cache import CacheAPI
    CacheAPI = CacheAPI

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The one-byte admission marker stored on the first miss of a key
    Marker = 'm'

    # Methods whose responses are cacheable without the body joining the key
    Safe_Methods = ('GET', 'HEAD')

    # The one method whose responses are cacheable when the body joins the key
    Body_Method = 'POST'

    # Response headers the cache adds
    Header_Cache = 'X-Cache'
    Header_Age   = 'Age'
    Header_ETag  = 'ETag'

    # Values of the X-Cache header
    Cache_Hit  = 'Hit'
    Cache_Miss = 'Miss'

    # Outcome labels of the per-channel metrics counter
    Outcome_Hit              = 'hit'
    Outcome_Miss             = 'miss'
    Outcome_Stored           = 'stored'
    Outcome_Marker_Stored    = 'marker_stored'
    Outcome_Coalesced        = 'coalesced'
    Outcome_Coalesce_Timeout = 'coalesce_timeout'
    Outcome_Bypass           = 'bypass'
    Outcome_Not_Modified     = 'not_modified'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ResponseCacheConfig:
    """ The parsed response caching configuration of one channel.
    """
    is_enabled: 'bool'
    ttl_seconds: 'int'
    is_shared_across_callers: 'bool'
    vary_by_headers: 'strlist'
    ignored_query_parameters: 'strlist'
    include_body_in_key: 'bool'
    max_body_size: 'int'
    cache_on_second_request: 'bool'
    needs_etag: 'bool'
    coalesce_timeout: 'float'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ResponseCacheContext:
    """ Everything one request needs to look up, store and coalesce its cached response.
    """
    cache_api: 'CacheAPI'
    config: 'ResponseCacheConfig'
    channel_id: 'int'
    channel_name: 'str'
    key: 'str'
    path_and_query: 'str'
    skip_lookup: 'bool'
    is_admitted: 'bool'
    if_none_match: 'str'
    wsgi_environ: 'stranydict'

# ################################################################################################################################
# ################################################################################################################################
