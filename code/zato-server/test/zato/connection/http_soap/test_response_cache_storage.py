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
from http.client import NOT_FOUND, NOT_MODIFIED, OK
from unittest import TestCase, main

# Zato
from zato.common.typing_ import any_, anydict
from zato.server.connection.http_soap.response_cache import get_context, lookup, purge_channel, store, \
    ResponseCacheContext

# Zato - test helpers
from test.zato.connection.http_soap.common import FakeCacheAPI, make_channel_item, make_environ, make_raw_config

# ################################################################################################################################
# ################################################################################################################################

class StorageRulesTestCase(TestCase):

    def setUp(self) -> 'None':
        self.cache = FakeCacheAPI()

    def get_ctx(self, raw_config:'anydict | None'=None, **environ_kwargs:'any_') -> 'ResponseCacheContext':
        if raw_config is None:
            raw_config = make_raw_config()
        channel_item = make_channel_item(raw_config)
        environ = make_environ(**environ_kwargs)
        ctx = get_context(self.cache, channel_item, environ, b'')
        assert ctx is not None

        return ctx

# ################################################################################################################################

    def test_store_and_lookup_round_trip(self) -> 'None':
        ctx = self.get_ctx()
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'

        store(ctx, '{"result":"ok"}', OK)

        # A fresh request context finds the stored entry
        ctx2 = self.get_ctx()
        out = lookup(ctx2)

        self.assertEqual(out, '{"result":"ok"}')

        headers = ctx2.wsgi_environ['zato.http.response.headers']
        self.assertEqual(headers['X-Cache'], 'Hit')
        self.assertIn('Age', headers)
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(ctx2.wsgi_environ['zato.http.response.status'], f'{OK} OK')

# ################################################################################################################################

    def test_lookup_miss_returns_none(self) -> 'None':
        ctx = self.get_ctx()
        out = lookup(ctx)
        self.assertIsNone(out)

# ################################################################################################################################

    def test_non_2xx_responses_are_never_stored(self) -> 'None':
        ctx = self.get_ctx()
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'

        store(ctx, '{"error":"not found"}', NOT_FOUND)

        self.assertEqual(self.cache.data, {})

# ################################################################################################################################

    def test_set_cookie_responses_are_never_stored(self) -> 'None':
        ctx = self.get_ctx()
        headers = ctx.wsgi_environ['zato.http.response.headers']
        headers['Content-Type'] = 'application/json'
        headers['Set-Cookie'] = 'session=abc'

        store(ctx, '{"result":"ok"}', OK)

        self.assertEqual(self.cache.data, {})

# ################################################################################################################################

    def test_responses_above_the_size_cap_are_never_stored(self) -> 'None':
        raw_config = make_raw_config(max_body_size=10)
        ctx = self.get_ctx(raw_config)
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'

        store(ctx, 'x' * 11, OK)

        self.assertEqual(self.cache.data, {})

# ################################################################################################################################

    def test_store_sets_the_miss_header(self) -> 'None':
        ctx = self.get_ctx()
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'

        store(ctx, '{"result":"ok"}', OK)

        headers = ctx.wsgi_environ['zato.http.response.headers']
        self.assertEqual(headers['X-Cache'], 'Miss')

# ################################################################################################################################

    def test_entry_ttl_matches_the_config(self) -> 'None':
        raw_config = make_raw_config(ttl=2, ttl_unit='minutes')
        ctx = self.get_ctx(raw_config)
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'

        store(ctx, '{"result":"ok"}', OK)

        self.assertEqual(self.cache.ttl[ctx.key], 120)

# ################################################################################################################################

    def test_no_cache_skips_the_lookup_but_still_stores(self) -> 'None':

        # An entry goes in first
        ctx = self.get_ctx()
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'
        store(ctx, '{"result":"stale"}', OK)

        # A no-cache request never reads it ..
        ctx2 = self.get_ctx(HTTP_CACHE_CONTROL='no-cache')
        self.assertTrue(ctx2.skip_lookup)

        out = lookup(ctx2)
        self.assertIsNone(out)

        # .. but its fresh response replaces the entry.
        ctx2.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'
        store(ctx2, '{"result":"fresh"}', OK)

        ctx3 = self.get_ctx()
        out = lookup(ctx3)
        self.assertEqual(out, '{"result":"fresh"}')

# ################################################################################################################################

    def test_purge_channel_empties_the_prefix(self) -> 'None':
        ctx = self.get_ctx()
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'
        store(ctx, '{"result":"ok"}', OK)

        self.assertEqual(len(self.cache.data), 1)

        purge_channel(self.cache, ctx.channel_id)

        self.assertEqual(self.cache.data, {})

# ################################################################################################################################
# ################################################################################################################################

class AdmissionTestCase(TestCase):
    """ Cache on second request - the first miss stores a marker, the second one stores the body.
    """

    def setUp(self) -> 'None':
        self.cache = FakeCacheAPI()
        self.raw_config = make_raw_config(cache_on_second_request=True)

    def get_ctx(self) -> 'ResponseCacheContext':
        channel_item = make_channel_item(self.raw_config)
        environ = make_environ()
        ctx = get_context(self.cache, channel_item, environ, b'')
        assert ctx is not None
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'

        return ctx

# ################################################################################################################################

    def test_marker_then_body_admission(self) -> 'None':

        # The first request misses and stores only the marker
        ctx1 = self.get_ctx()
        self.assertIsNone(lookup(ctx1))
        self.assertFalse(ctx1.is_admitted)

        store(ctx1, '{"result":"first"}', OK)
        self.assertEqual(self.cache.get(ctx1.key), 'm')

        # The second request finds the marker - still a miss, but now admitted
        ctx2 = self.get_ctx()
        self.assertIsNone(lookup(ctx2))
        self.assertTrue(ctx2.is_admitted)

        store(ctx2, '{"result":"second"}', OK)

        # The third request is a hit
        ctx3 = self.get_ctx()
        out = lookup(ctx3)
        self.assertEqual(out, '{"result":"second"}')

# ################################################################################################################################

    def test_admission_off_stores_on_first_miss(self) -> 'None':
        self.raw_config = make_raw_config(cache_on_second_request=False)

        ctx1 = self.get_ctx()
        self.assertIsNone(lookup(ctx1))

        store(ctx1, '{"result":"first"}', OK)

        ctx2 = self.get_ctx()
        out = lookup(ctx2)
        self.assertEqual(out, '{"result":"first"}')

# ################################################################################################################################
# ################################################################################################################################

class ETagTestCase(TestCase):

    def setUp(self) -> 'None':
        self.cache = FakeCacheAPI()
        self.raw_config = make_raw_config(needs_etag=True)

    def get_ctx(self, **environ_kwargs:'any_') -> 'ResponseCacheContext':
        channel_item = make_channel_item(self.raw_config)
        environ = make_environ(**environ_kwargs)
        ctx = get_context(self.cache, channel_item, environ, b'')
        assert ctx is not None
        ctx.wsgi_environ['zato.http.response.headers']['Content-Type'] = 'application/json'

        return ctx

# ################################################################################################################################

    def test_etag_round_trip(self) -> 'None':

        # Store a response - the entry carries an ETag
        ctx1 = self.get_ctx()
        store(ctx1, '{"result":"ok"}', OK)

        # A plain lookup returns the body along with the ETag header
        ctx2 = self.get_ctx()
        out = lookup(ctx2)
        self.assertEqual(out, '{"result":"ok"}')

        etag = ctx2.wsgi_environ['zato.http.response.headers']['ETag']
        self.assertTrue(etag)

        # A request carrying the matching ETag gets a bodyless 304
        ctx3 = self.get_ctx(HTTP_IF_NONE_MATCH=etag)
        out = lookup(ctx3)
        self.assertEqual(out, '')
        self.assertTrue(ctx3.wsgi_environ['zato.http.response.status'].startswith(f'{NOT_MODIFIED}'))

        # A request with a stale ETag gets the full body
        ctx4 = self.get_ctx(HTTP_IF_NONE_MATCH='"stale"')
        out = lookup(ctx4)
        self.assertEqual(out, '{"result":"ok"}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
