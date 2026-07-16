# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.common.api import URL_TYPE
from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class FakeCacheAPI:
    """ An in-memory stand-in for the Redis-backed CacheAPI, JSON round-tripping values the same way.
    """
    def __init__(self) -> 'None':
        self.data:'anydict' = {}
        self.ttl:'anydict' = {}

    def get(self, key:'str') -> 'any_':
        if key in self.data:
            return loads(self.data[key])
        return None

    def set(self, key:'str', value:'any_', expiry:'int'=0) -> 'None':
        self.data[key] = dumps(value)
        self.ttl[key] = expiry

    def delete_by_prefix(self, prefix:'str') -> 'None':
        for key in list(self.data):
            if key.startswith(prefix):
                del self.data[key]
                del self.ttl[key]

# ################################################################################################################################
# ################################################################################################################################

def make_raw_config(**overrides:'any_') -> 'anydict':
    out = {
        'is_enabled': True,
        'ttl': 60,
        'ttl_unit': 'seconds',
        'is_shared_across_callers': False,
        'vary_by_headers': [],
        'ignored_query_parameters': [],
        'include_body_in_key': False,
        'max_body_size': 1000,
        'cache_on_second_request': False,
        'needs_etag': False,
        'coalesce_timeout': 5,
    }
    out.update(overrides)

    return out

# ################################################################################################################################

def make_channel_item(raw_config:'anydict', transport:'str'=URL_TYPE.PLAIN_HTTP, channel_id:'int'=123) -> 'anydict':
    out = {
        'id': channel_id,
        'name': 'test.channel',
        'transport': transport,
        'response_cache': raw_config,
    }

    return out

# ################################################################################################################################

def make_environ(method:'str'='GET', path:'str'='/api/customers', query:'str'='', sec_def_name:'str'='',
    **extra:'any_') -> 'anydict':
    out:'anydict' = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': query,
        'zato.http.response.headers': {},
    }

    if sec_def_name:
        out['zato.sec_def'] = {'name': sec_def_name}

    out.update(extra)

    return out

# ################################################################################################################################
# ################################################################################################################################
