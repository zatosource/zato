# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# Zato
from zato.common.api import URL_TYPE
from zato.common.typing_ import any_, anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

class FakeCacheAPI:
    """ An in-memory stand-in for the Redis-backed CacheAPI, JSON round-tripping values the same way.
    """
    def __init__(self) -> 'None':
        self.data:'anydict' = {}
        self.ttl:'anydict' = {}
        self.counters:'anydict' = {}

    def get(self, key:'str') -> 'any_':
        if key in self.data:
            return loads(self.data[key])
        return None

    def set(self, key:'str', value:'any_', expiry:'int'=0) -> 'None':
        self.data[key] = dumps(value)
        self.ttl[key] = expiry

    def get_counter(self, counter_key:'str') -> 'int':
        if counter_key in self.counters:
            return self.counters[counter_key]
        return 0

    def get_with_counter(self, key:'str', counter_key:'str') -> 'anytuple':
        out = (self.get(key), self.get_counter(counter_key))
        return out

    def increment_counter(self, counter_key:'str') -> 'int':
        self.counters[counter_key] = self.get_counter(counter_key) + 1
        return self.counters[counter_key]

    def set_if_counter(self, key:'str', value:'any_', expiry:'int', counter_key:'str', counter:'int') -> 'bool':
        if self.get_counter(counter_key) != counter:
            return False
        self.set(key, value, expiry)
        return True

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
