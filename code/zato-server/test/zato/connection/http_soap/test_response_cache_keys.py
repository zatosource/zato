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
from unittest import TestCase, main

# Zato
from zato.common.api import URL_TYPE
from zato.common.typing_ import any_, anydict
from zato.server.connection.http_soap.response_cache import get_context

# Zato - test helpers
from test.zato.connection.http_soap.common import FakeCacheAPI, make_channel_item, make_environ, make_raw_config

# ################################################################################################################################
# ################################################################################################################################

class KeyConstructionTestCase(TestCase):

    def setUp(self) -> 'None':
        self.cache = FakeCacheAPI()

    def get_key(self, raw_config:'anydict | None'=None, transport:'str'=URL_TYPE.PLAIN_HTTP, payload:'bytes'=b'',
        **environ_kwargs:'any_') -> 'str':
        if raw_config is None:
            raw_config = make_raw_config()
        channel_item = make_channel_item(raw_config, transport)
        environ = make_environ(**environ_kwargs)
        ctx = get_context(self.cache, channel_item, environ, payload)
        assert ctx is not None

        return ctx.key

# ################################################################################################################################

    def test_query_parameter_order_never_splits_the_cache(self) -> 'None':
        key1 = self.get_key(query='a=1&b=2')
        key2 = self.get_key(query='b=2&a=1')
        self.assertEqual(key1, key2)

# ################################################################################################################################

    def test_query_parameter_values_vary_the_key(self) -> 'None':
        key1 = self.get_key(query='a=1')
        key2 = self.get_key(query='a=2')
        self.assertNotEqual(key1, key2)

# ################################################################################################################################

    def test_ignored_query_parameters_never_vary_the_key(self) -> 'None':
        raw_config = make_raw_config(ignored_query_parameters=['utm_source', 'utm_medium'])

        key1 = self.get_key(raw_config, query='a=1&utm_source=news&utm_medium=email')
        key2 = self.get_key(raw_config, query='a=1')
        self.assertEqual(key1, key2)

# ################################################################################################################################

    def test_caller_identity_varies_the_key_by_default(self) -> 'None':
        key1 = self.get_key(sec_def_name='caller.1')
        key2 = self.get_key(sec_def_name='caller.2')
        self.assertNotEqual(key1, key2)

# ################################################################################################################################

    def test_shared_across_callers_removes_identity_from_the_key(self) -> 'None':
        raw_config = make_raw_config(is_shared_across_callers=True)

        key1 = self.get_key(raw_config, sec_def_name='caller.1')
        key2 = self.get_key(raw_config, sec_def_name='caller.2')
        self.assertEqual(key1, key2)

# ################################################################################################################################

    def test_vary_by_headers_vary_the_key(self) -> 'None':
        raw_config = make_raw_config(vary_by_headers=['Accept-Language'])

        key1 = self.get_key(raw_config, HTTP_ACCEPT_LANGUAGE='en')
        key2 = self.get_key(raw_config, HTTP_ACCEPT_LANGUAGE='de')
        self.assertNotEqual(key1, key2)

# ################################################################################################################################

    def test_unlisted_headers_never_vary_the_key(self) -> 'None':
        key1 = self.get_key(HTTP_ACCEPT_LANGUAGE='en')
        key2 = self.get_key(HTTP_ACCEPT_LANGUAGE='de')
        self.assertEqual(key1, key2)

# ################################################################################################################################

    def test_body_hash_varies_the_key_for_post(self) -> 'None':
        raw_config = make_raw_config(include_body_in_key=True)

        key1 = self.get_key(raw_config, method='POST', payload=b'{"a":1}')
        key2 = self.get_key(raw_config, method='POST', payload=b'{"a":2}')
        self.assertNotEqual(key1, key2)

# ################################################################################################################################

    def test_channel_id_varies_the_key(self) -> 'None':
        channel_item_1 = make_channel_item(make_raw_config(), channel_id=1)
        channel_item_2 = make_channel_item(make_raw_config(), channel_id=2)

        ctx1 = get_context(self.cache, channel_item_1, make_environ(), b'')
        ctx2 = get_context(self.cache, channel_item_2, make_environ(), b'')

        assert ctx1 is not None
        assert ctx2 is not None

        self.assertNotEqual(ctx1.key, ctx2.key)

# ################################################################################################################################

    def test_post_without_body_in_key_is_not_cacheable(self) -> 'None':
        channel_item = make_channel_item(make_raw_config())
        ctx = get_context(self.cache, channel_item, make_environ(method='POST'), b'{}')
        self.assertIsNone(ctx)

# ################################################################################################################################

    def test_request_body_above_the_cap_bypasses_caching(self) -> 'None':
        raw_config = make_raw_config(include_body_in_key=True, max_body_size=10)
        channel_item = make_channel_item(raw_config)

        ctx = get_context(self.cache, channel_item, make_environ(method='POST'), b'x' * 11)
        self.assertIsNone(ctx)

# ################################################################################################################################

    def test_disabled_config_yields_no_context(self) -> 'None':
        channel_item = make_channel_item(make_raw_config(is_enabled=False))
        ctx = get_context(self.cache, channel_item, make_environ(), b'')
        self.assertIsNone(ctx)

# ################################################################################################################################

    def test_channel_without_config_yields_no_context(self) -> 'None':
        channel_item = {'id': 1, 'name': 'test.channel', 'transport': URL_TYPE.PLAIN_HTTP}
        ctx = get_context(self.cache, channel_item, make_environ(), b'')
        self.assertIsNone(ctx)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
