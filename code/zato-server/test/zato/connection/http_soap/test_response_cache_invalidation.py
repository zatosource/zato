# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - must run before threading is imported by the module under test
from gevent import monkey

if not monkey.is_module_patched('threading'):
    _ = monkey.patch_all()

# stdlib
from http.client import OK
from unittest import TestCase, main

# Zato
from zato.common.typing_ import any_, anydict, anylist, cast_
from zato.server.connection import cache as cache_module
from zato.server.connection.cache import CacheAPI
from zato.server.connection.http_soap.response_cache import get_context, lookup, store, ResponseCacheContext

# Zato - test helpers
from test.zato.connection.http_soap.common import make_channel_item, make_environ, make_raw_config

# ################################################################################################################################
# ################################################################################################################################

class FakeRedis:
    """ A fake Redis exposing just what CacheAPI needs.
    """
    def __init__(self) -> 'None':
        self.data:'anydict' = {}

    def get(self, key:'str') -> 'any_':
        return self.data.get(key)

    def set(self, key:'str', value:'any_', ex:'any_'=None) -> 'None':
        self.data[key] = value

    def delete(self, key:'str') -> 'None':
        if key in self.data:
            del self.data[key]

    def exists(self, key:'str') -> 'int':
        return int(key in self.data)

    def scan_iter(self, match:'str') -> 'any_':
        prefix = match[:-1]
        for key in list(self.data):
            if key.startswith(prefix):
                yield key

    def mget(self, keys:'anylist') -> 'anylist':
        out = [self.data.get(key) for key in keys]
        return out

    def incr(self, key:'str') -> 'int':
        out = int(self.data.get(key, 0)) + 1
        self.data[key] = str(out)
        return out

    def register_script(self, script:'str') -> 'any_':
        if script == cache_module.ModuleCtx.Set_If_Counter_Script:
            return self._set_if_counter
        return self._delete_if_value

    def _set_if_counter(self, keys:'anylist', args:'anylist') -> 'int':
        key, counter_key = keys
        counter, serialized, _expiry = args
        if int(self.data.get(counter_key, 0)) != counter:
            return 0
        self.data[key] = serialized
        return 1

    def _delete_if_value(self, keys:'anylist', args:'anylist') -> 'int':
        key = keys[0]
        if self.data.get(key) != args[0]:
            return 0
        del self.data[key]
        return 1

# ################################################################################################################################
# ################################################################################################################################

class FakeConfigManager:
    """ Resolves the one channel name the tests use to its ID, the way ConfigManager does.
    """
    def get_channel_rest(self, name:'str') -> 'anydict | None':
        if name == 'test.channel':
            return {'id': 123, 'name': name}

# ################################################################################################################################
# ################################################################################################################################

class InvalidationTestCase(TestCase):
    """ Programmatic invalidation over the CacheAPI facade, backed by a fake config manager.
    """

    def setUp(self) -> 'None':
        self.fake_redis = FakeRedis()
        self.cache_api = CacheAPI(cast_('any_', self.fake_redis), config_manager=cast_('any_', FakeConfigManager()))

    def store_entry(self, path:'str', query:'str'='') -> 'ResponseCacheContext':
        channel_item = make_channel_item(make_raw_config())
        environ = make_environ(path=path, query=query)
        ctx = get_context(self.cache_api, channel_item, environ, b'')
        assert ctx is not None
        _ = lookup(ctx)
        ctx.request_ctx['zato.http.response.headers']['Content-Type'] = 'application/json'
        store(ctx, '{"result":"ok"}', OK)

        return ctx

# ################################################################################################################################

    def test_invalidate_whole_channel(self) -> 'None':
        _ = self.store_entry('/api/customers')
        _ = self.store_entry('/api/orders')

        self.cache_api.invalidate_response('test.channel')

        # Only the generation of the channel remains, outside the key space of its responses
        generation_key = 'zato:cache:' + cache_module.ModuleCtx.Response_Generation_Key.format(123)
        self.assertEqual(list(self.fake_redis.data), [generation_key])
        self.assertEqual(self.fake_redis.data[generation_key], '1')

# ################################################################################################################################

    def test_invalidate_by_pattern(self) -> 'None':
        ctx_customers = self.store_entry('/api/customers', 'a=1')
        ctx_orders = self.store_entry('/api/orders')

        self.cache_api.invalidate_response('test.channel', '/api/customers*')

        self.assertIsNone(self.cache_api.get(ctx_customers.key))
        self.assertIsNotNone(self.cache_api.get(ctx_orders.key))

# ################################################################################################################################

    def test_invalidate_unknown_channel_raises(self) -> 'None':
        with self.assertRaises(Exception) as exc_ctx:
            self.cache_api.invalidate_response('no.such.channel')

        self.assertIn('no.such.channel', str(exc_ctx.exception))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
