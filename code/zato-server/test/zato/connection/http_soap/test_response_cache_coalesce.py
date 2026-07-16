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
import random
from json import dumps, loads
from time import time
from unittest import TestCase, main

# gevent
import gevent
from gevent import sleep, spawn, Timeout
from gevent.event import Event

# Zato
from zato.common.typing_ import any_, anydict, strlist
from zato.server.connection.http_soap.response_cache import coalesce
from zato.server.connection.http_soap.response_cache import counters, invoke_coalesced, ResponseCacheConfig, \
    ResponseCacheContext

# ################################################################################################################################
# ################################################################################################################################

class FakeCacheAPI:
    """ An in-memory stand-in for the Redis-backed CacheAPI, JSON round-tripping values the same way.
    """
    def __init__(self) -> 'None':
        self.data:'anydict' = {}

    def get(self, key:'str') -> 'any_':
        if key in self.data:
            return loads(self.data[key])
        return None

    def set(self, key:'str', value:'any_', expiry:'int'=0) -> 'None':
        self.data[key] = dumps(value)

# ################################################################################################################################

def make_ctx(cache_api:'any_', key:'str', is_admitted:'bool', coalesce_timeout:'float'=5) -> 'ResponseCacheContext':

    config = ResponseCacheConfig()
    config.is_enabled = True
    config.ttl_seconds = 60
    config.is_shared_across_callers = False
    config.vary_by_headers = []
    config.ignored_query_parameters = []
    config.include_body_in_key = False
    config.max_body_size = 1_000_000
    config.cache_on_second_request = True
    config.needs_etag = False
    config.coalesce_timeout = coalesce_timeout

    ctx = ResponseCacheContext()
    ctx.cache_api = cache_api
    ctx.config = config
    ctx.channel_id = 1
    ctx.channel_name = 'test.coalesce'
    ctx.key = key
    ctx.path_and_query = '/test'
    ctx.skip_lookup = False
    ctx.is_admitted = is_admitted
    ctx.if_none_match = ''
    ctx.wsgi_environ = {'zato.http.response.headers': {}}

    return ctx

# ################################################################################################################################

def make_entry(body:'str') -> 'anydict':
    out = {
        'body': body,
        'content_type': 'application/json',
        'status_code': 200,
        'stored_at': time(),
        'etag': '',
        'path': '/test',
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

class CoalescingBaseTestCase(TestCase):

    def setUp(self) -> 'None':
        counters.reset()
        coalesce._key_locks.clear()
        self.cache = FakeCacheAPI()

    def assert_lock_dict_empty(self) -> 'None':
        self.assertEqual(coalesce._key_locks, {})

# ################################################################################################################################
# ################################################################################################################################

class InterleavingTestCase(CoalescingBaseTestCase):
    """ Choreographed interleaving of greenlets through the coalescing yield points.
    """

    def test_waiter_is_served_after_the_holder_stores(self) -> 'None':

        key = 'test.key.1'
        holder_started = Event()
        holder_proceed = Event()

        # The holder blocks inside its invocation until the test says otherwise,
        # then stores the entry the way channel.py's invoke path does.
        def holder_invoke() -> 'str':
            holder_started.set()
            _ = holder_proceed.wait()
            self.cache.set(key, make_entry('holder-body'))
            return 'holder-body'

        # The waiter must be served from the cache, never invoked
        def waiter_invoke() -> 'None':
            raise AssertionError('The waiter must never invoke the service')

        holder_ctx = make_ctx(self.cache, key, is_admitted=True)
        waiter_ctx = make_ctx(self.cache, key, is_admitted=True)

        holder = spawn(invoke_coalesced, holder_ctx, holder_invoke, ())
        _ = holder_started.wait()

        # The holder now owns the key's lock - the waiter blocks on it
        waiter = spawn(invoke_coalesced, waiter_ctx, waiter_invoke, ())
        sleep(0.05)

        holder_proceed.set()
        _ = holder.join()
        _ = waiter.join()

        self.assertEqual(holder.value, 'holder-body')
        self.assertEqual(waiter.value, 'holder-body')

        # One invocation, one coalesced request, nothing stranded
        self.assertEqual(counters.invoke_count, 1)
        self.assertEqual(counters.coalesced_count, 1)
        self.assertEqual(counters.coalesce_timeout_count, 0)

        self.assert_lock_dict_empty()

# ################################################################################################################################

    def test_waiter_timeout_degrades_to_uncoalesced(self) -> 'None':

        key = 'test.key.2'
        holder_started = Event()
        holder_proceed = Event()

        def holder_invoke():
            holder_started.set()
            _ = holder_proceed.wait()
            self.cache.set(key, make_entry('holder-body'))
            return 'holder-body'

        # This time the waiter does invoke - its acquire times out below
        def waiter_invoke() -> 'str':
            return 'waiter-body'

        holder_ctx = make_ctx(self.cache, key, is_admitted=True)
        waiter_ctx = make_ctx(self.cache, key, is_admitted=True, coalesce_timeout=0.05)

        holder = spawn(invoke_coalesced, holder_ctx, holder_invoke, ())
        _ = holder_started.wait()

        waiter = spawn(invoke_coalesced, waiter_ctx, waiter_invoke, ())
        _ = waiter.join()

        # The waiter timed out and served itself while the holder still runs
        self.assertEqual(waiter.value, 'waiter-body')
        self.assertEqual(counters.coalesce_timeout_count, 1)

        holder_proceed.set()
        _ = holder.join()

        self.assertEqual(holder.value, 'holder-body')

        # Both requests invoked - a slow service degrades to uncoalesced behavior
        self.assertEqual(counters.invoke_count, 2)
        self.assertEqual(counters.coalesced_count, 0)

        self.assert_lock_dict_empty()

# ################################################################################################################################

    def test_holder_exception_releases_the_lock(self) -> 'None':

        key = 'test.key.3'
        holder_started = Event()
        holder_proceed = Event()

        def holder_invoke() -> 'None':
            holder_started.set()
            _ = holder_proceed.wait()
            raise Exception('The service failed')

        # The cache stays empty, so the waiter invokes after acquiring the released lock
        def waiter_invoke() -> 'str':
            return 'waiter-body'

        holder_ctx = make_ctx(self.cache, key, is_admitted=True)
        waiter_ctx = make_ctx(self.cache, key, is_admitted=True)

        holder = spawn(invoke_coalesced, holder_ctx, holder_invoke, ())
        _ = holder_started.wait()

        waiter = spawn(invoke_coalesced, waiter_ctx, waiter_invoke, ())
        sleep(0.05)

        holder_proceed.set()
        _ = holder.join()
        _ = waiter.join()

        # The holder failed but nobody was stranded
        self.assertIsNotNone(holder.exception)
        self.assertEqual(waiter.value, 'waiter-body')

        self.assertEqual(counters.invoke_count, 2)
        self.assertEqual(counters.coalesce_timeout_count, 0)

        self.assert_lock_dict_empty()

# ################################################################################################################################

    def test_recheck_window_serves_from_the_cache(self) -> 'None':

        key = 'test.key.4'

        # The entry lands in the cache between the fast-path read and the acquire -
        # simulated here by pre-filling the cache before the call.
        self.cache.set(key, make_entry('cached-body'))

        def never_invoke() -> 'None':
            raise AssertionError('The re-check must serve from the cache')

        ctx = make_ctx(self.cache, key, is_admitted=True)
        out = invoke_coalesced(ctx, never_invoke, ())

        self.assertEqual(out, 'cached-body')
        self.assertEqual(counters.invoke_count, 0)
        self.assertEqual(counters.coalesced_count, 1)

        self.assert_lock_dict_empty()

# ################################################################################################################################

    def test_non_admitted_requests_run_in_parallel(self) -> 'None':

        key = 'test.key.5'

        both_inside = Event()
        first_inside = Event()

        # Both invocations must be inside the service at the same time -
        # proof that no lock serializes first-ever requests.
        def invoke_one() -> 'str':
            first_inside.set()
            _ = both_inside.wait()
            return 'one'

        def invoke_two() -> 'str':
            _ = first_inside.wait()
            both_inside.set()
            return 'two'

        ctx1 = make_ctx(self.cache, key, is_admitted=False)
        ctx2 = make_ctx(self.cache, key, is_admitted=False)

        greenlet1 = spawn(invoke_coalesced, ctx1, invoke_one, ())
        greenlet2 = spawn(invoke_coalesced, ctx2, invoke_two, ())

        with Timeout(5):
            _ = greenlet1.join()
            _ = greenlet2.join()

        self.assertEqual(greenlet1.value, 'one')
        self.assertEqual(greenlet2.value, 'two')

        self.assertEqual(counters.invoke_count, 2)
        self.assertEqual(counters.coalesced_count, 0)

        # Non-admitted requests never touch the lock dict
        self.assert_lock_dict_empty()

# ################################################################################################################################
# ################################################################################################################################

class StressTestCase(CoalescingBaseTestCase):
    """ Invariant stress test - many greenlets, few keys, random service latency.
    """

    def test_stress_invariants(self) -> 'None':

        key_count = 5
        greenlet_count = 1000

        keys:'strlist' = []

        for idx in range(key_count):
            keys.append(f'stress.key.{idx}')

        def make_invoke(key:'str') -> 'any_':
            def invoke() -> 'str':
                # A random service latency shuffles the interleavings
                sleep(random.random() / 500)
                body = f'body-{key}'
                self.cache.set(key, make_entry(body))
                return body
            return invoke

        def run_one(key:'str') -> 'any_':
            ctx = make_ctx(self.cache, key, is_admitted=True, coalesce_timeout=30)
            out = invoke_coalesced(ctx, make_invoke(key), ())
            return key, out

        greenlets = []
        for idx in range(greenlet_count):
            key = keys[idx % key_count]
            greenlets.append(spawn(run_one, key))

        # Completion is an invariant of its own - a deadlock trips this timeout
        with Timeout(30):
            _ = gevent.joinall(greenlets, raise_error=True)

        # No cross-key leakage - every request got the body of its own key
        for greenlet in greenlets:
            key, out = greenlet.value
            self.assertEqual(out, f'body-{key}')

        # Exactly one invocation per key - the first holder stores the entry under the lock,
        # everyone after it is served from the cache.
        self.assertEqual(counters.invoke_count, key_count)
        self.assertEqual(counters.coalesce_timeout_count, 0)
        self.assertEqual(counters.coalesced_count, greenlet_count - key_count)

        # The cleanup invariant - the per-key lock dict never outlives its requests
        self.assert_lock_dict_empty()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
