# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import copy
from importlib import import_module
from types import SimpleNamespace

# gevent
from gevent import joinall, sleep, spawn
from gevent.event import Event

# Zato
from zato.server.connection.http_soap import response_cache as response_cache_module

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import any_, anydict, anylist
    from zato.server.connection.cache import CacheAPI
    from zato.server.connection.http_soap.response_cache.common import ResponseCacheContext

    anydict = anydict
    anylist = anylist
    CacheAPI = CacheAPI
    Redis = Redis
    ResponseCacheContext = ResponseCacheContext

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Channel_ID = 1
    Channel_Name = 'test.response.cache.workers'

    # The coalesce timeout of the channel, in seconds, and a shorter one for the test of a waiter that times out
    Coalesce_Timeout = 15
    Short_Coalesce_Timeout = 1

    # How many requests wait for the holder, spread over two connections to Redis, one per worker
    Waiter_Count = 4

    # How long the waiters run before the holder proceeds, in seconds
    Waiter_Head_Start = 0.2

    # How long the test waits for a request, in seconds
    Request_Timeout = 20.0

# ################################################################################################################################
# ################################################################################################################################

# The cache API of this tree, which replaces the module of the main repository under its name
cache_module = import_module('zato.server.connection.cache')

# ################################################################################################################################
# ################################################################################################################################

class _Matcher:
    """ An object of a channel item whose representation differs between processes.
    """

# ################################################################################################################################
# ################################################################################################################################

def _new_cache_api(redis_conn:'Redis') -> 'CacheAPI':
    """ Returns a cache API with a connection of its own, as each worker has.
    """

    # Redis
    from redis import Redis

    connection_kwargs = redis_conn.connection_pool.connection_kwargs
    redis_client = Redis(host=connection_kwargs['host'], port=connection_kwargs['port'], decode_responses=True)

    channel = {'id': ModuleCtx.Channel_ID, 'name': ModuleCtx.Channel_Name}

    def get_channel_rest(name:'str') -> 'anydict':
        return channel

    config_manager = SimpleNamespace(get_channel_rest=get_channel_rest)

    out = cache_module.CacheAPI(redis_client, config_manager) # type: ignore[arg-type]
    return out

# ################################################################################################################################

def _new_channel_item(cache_on_second_request:'bool', coalesce_timeout:'int', service_name:'str'='test.service') -> 'anydict':
    """ Returns a channel item as url_data builds it, with an object that differs between processes.
    """
    out = {
        'id': ModuleCtx.Channel_ID,
        'name': ModuleCtx.Channel_Name,
        'transport': 'plain_http',
        'service_name': service_name,
        'match_target_compiled': _Matcher(),
        'response_cache': {
            'is_enabled': True,
            'cache_on_second_request': cache_on_second_request,
            'coalesce_timeout': coalesce_timeout,
        },
    }
    return out

# ################################################################################################################################

def _new_context(cache_api:'CacheAPI', channel_item:'anydict') -> 'ResponseCacheContext':
    """ Builds the context of one GET request, as the channel does for each request it dispatches.
    """
    request_ctx = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/api/customers',
        'QUERY_STRING': '',
        'zato.http.response.headers': {'Content-Type': 'application/json'},
    }

    out = response_cache_module.get_context(cache_api, channel_item, request_ctx, b'')
    assert out is not None

    return out

# ################################################################################################################################

def _store_body(ctx:'ResponseCacheContext', body:'str') -> 'str':
    """ Stores the response of a request, as the channel does in _format_response.
    """
    response_cache_module.store(ctx, body, 200)
    return body

# ################################################################################################################################

def _request(cache_api:'CacheAPI', channel_item:'anydict', invoke:'any_') -> 'any_':
    """ Runs one request through the lookup and, on a miss, through coalescing.
    """
    ctx = _new_context(cache_api, channel_item)

    out = response_cache_module.lookup(ctx)

    if out is None:
        out = response_cache_module.invoke_coalesced(ctx, invoke, (ctx,))

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_requests_of_two_workers_invoke_the_service_once(redis_conn:'Redis') -> 'None':
    """ Concurrent requests of one admitted key, through two connections to Redis, are served one invocation.
    """
    response_cache_module.counters.reset()

    workers = [_new_cache_api(redis_conn), _new_cache_api(redis_conn)]
    channel_item = _new_channel_item(True, ModuleCtx.Coalesce_Timeout)

    # The key repeated once already, so it holds the admission marker
    marker_ctx = _new_context(workers[0], channel_item)
    workers[0].set(marker_ctx.key, response_cache_module.ModuleCtx.Marker, marker_ctx.config.ttl_seconds)

    holder_started = Event()
    holder_proceed = Event()

    def holder_invoke(ctx:'ResponseCacheContext') -> 'str':
        holder_started.set()
        _ = holder_proceed.wait()
        out = _store_body(ctx, 'holder-body')
        return out

    def waiter_invoke(ctx:'ResponseCacheContext') -> 'None':
        raise AssertionError('A waiter must never invoke the service')

    holder = spawn(_request, workers[0], channel_item, holder_invoke)
    _ = holder_started.wait(ModuleCtx.Request_Timeout)

    waiters:'anylist' = []

    for idx in range(ModuleCtx.Waiter_Count):
        worker = workers[idx % len(workers)]
        waiters.append(spawn(_request, worker, channel_item, waiter_invoke))

    # Every waiter polls a few times before the holder stores its entry
    sleep(ModuleCtx.Waiter_Head_Start)

    holder_proceed.set()
    _ = joinall([holder, *waiters], timeout=ModuleCtx.Request_Timeout, raise_error=True)

    assert holder.value == 'holder-body'
    assert [waiter.value for waiter in waiters] == ['holder-body'] * ModuleCtx.Waiter_Count

    assert response_cache_module.counters.invoke_count == 1
    assert response_cache_module.counters.coalesced_count == ModuleCtx.Waiter_Count
    assert response_cache_module.counters.coalesce_timeout_count == 0

    # The holder released its lock
    lock_key = cache_module.ModuleCtx.Response_Lock_Prefix + marker_ctx.key
    assert not workers[0].exists(lock_key)

# ################################################################################################################################

def test_first_requests_of_a_channel_storing_on_the_first_miss_invoke_the_service_once(redis_conn:'Redis') -> 'None':
    """ With Cache on second request off, concurrent first requests of a key are served one invocation.
    """
    response_cache_module.counters.reset()

    cache_api = _new_cache_api(redis_conn)
    channel_item = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)

    holder_started = Event()
    holder_proceed = Event()

    def holder_invoke(ctx:'ResponseCacheContext') -> 'str':
        holder_started.set()
        _ = holder_proceed.wait()
        out = _store_body(ctx, 'first-body')
        return out

    def waiter_invoke(ctx:'ResponseCacheContext') -> 'None':
        raise AssertionError('A waiter must never invoke the service')

    holder = spawn(_request, cache_api, channel_item, holder_invoke)
    _ = holder_started.wait(ModuleCtx.Request_Timeout)

    waiter = spawn(_request, cache_api, channel_item, waiter_invoke)
    sleep(ModuleCtx.Waiter_Head_Start)

    holder_proceed.set()
    _ = joinall([holder, waiter], timeout=ModuleCtx.Request_Timeout, raise_error=True)

    assert waiter.value == 'first-body'
    assert response_cache_module.counters.invoke_count == 1
    assert response_cache_module.counters.coalesced_count == 1

# ################################################################################################################################

def test_waiter_invokes_the_service_after_the_timeout(redis_conn:'Redis') -> 'None':
    """ A request that waited for the whole coalesce timeout invokes the service itself.
    """
    response_cache_module.counters.reset()

    cache_api = _new_cache_api(redis_conn)
    channel_item = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)

    holder_started = Event()
    holder_proceed = Event()

    def holder_invoke(ctx:'ResponseCacheContext') -> 'str':
        holder_started.set()
        _ = holder_proceed.wait()
        return 'holder-body'

    def waiter_invoke(ctx:'ResponseCacheContext') -> 'str':
        return 'waiter-body'

    holder = spawn(_request, cache_api, channel_item, holder_invoke)
    _ = holder_started.wait(ModuleCtx.Request_Timeout)

    # The waiter waits for less time than the lock of the holder lives
    waiter_ctx = _new_context(cache_api, channel_item)
    assert response_cache_module.lookup(waiter_ctx) is None

    waiter_ctx.config = copy(waiter_ctx.config)
    waiter_ctx.config.coalesce_timeout = ModuleCtx.Short_Coalesce_Timeout

    waiter = spawn(response_cache_module.invoke_coalesced, waiter_ctx, waiter_invoke, (waiter_ctx,))
    _ = waiter.join(ModuleCtx.Request_Timeout)

    assert waiter.value == 'waiter-body'
    assert response_cache_module.counters.coalesce_timeout_count == 1

    holder_proceed.set()
    _ = holder.join(ModuleCtx.Request_Timeout)

    assert holder.value == 'holder-body'
    assert response_cache_module.counters.invoke_count == 2

# ################################################################################################################################

def test_holder_exception_hands_the_lock_to_a_waiter(redis_conn:'Redis') -> 'None':
    """ A holder whose service raised an exception releases the lock, and a waiter invokes the service in its place.
    """
    response_cache_module.counters.reset()

    cache_api = _new_cache_api(redis_conn)
    channel_item = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)

    holder_started = Event()
    holder_proceed = Event()

    def holder_invoke(ctx:'ResponseCacheContext') -> 'None':
        holder_started.set()
        _ = holder_proceed.wait()
        raise Exception('The service failed')

    def waiter_invoke(ctx:'ResponseCacheContext') -> 'str':
        out = _store_body(ctx, 'waiter-body')
        return out

    holder = spawn(_request, cache_api, channel_item, holder_invoke)
    _ = holder_started.wait(ModuleCtx.Request_Timeout)

    waiter = spawn(_request, cache_api, channel_item, waiter_invoke)
    sleep(ModuleCtx.Waiter_Head_Start)

    holder_proceed.set()
    _ = joinall([holder, waiter], timeout=ModuleCtx.Request_Timeout)

    assert holder.exception is not None
    assert waiter.value == 'waiter-body'
    assert response_cache_module.counters.invoke_count == 2
    assert response_cache_module.counters.coalesce_timeout_count == 0

# ################################################################################################################################

def test_holder_never_deletes_the_lock_of_another_holder(redis_conn:'Redis') -> 'None':
    """ A holder whose lock expired and was taken by another request leaves that request's lock in place.
    """
    cache_api = _new_cache_api(redis_conn)
    lock_key = cache_module.ModuleCtx.Response_Lock_Prefix + 'key'

    assert cache_api.set_if_absent(lock_key, 'first', ModuleCtx.Coalesce_Timeout)

    # The lock of the first holder expires ..
    cache_api.delete(lock_key)

    # .. a second holder takes it ..
    assert cache_api.set_if_absent(lock_key, 'second', ModuleCtx.Coalesce_Timeout)

    # .. and the first holder releases only its own.
    assert not cache_api.delete_if_value(lock_key, 'first')
    assert cache_api.get(lock_key) == 'second'

    assert cache_api.delete_if_value(lock_key, 'second')
    assert not cache_api.exists(lock_key)

# ################################################################################################################################

def test_zero_timeout_invokes_the_service_without_a_lock(redis_conn:'Redis') -> 'None':
    """ Without a coalesce timeout, an admitted request invokes the service and stores no lock key.
    """
    response_cache_module.counters.reset()

    cache_api = _new_cache_api(redis_conn)
    channel_item = _new_channel_item(False, 0)
    lock_keys:'anylist' = []

    def invoke(ctx:'ResponseCacheContext') -> 'str':
        lock_key = cache_module.ModuleCtx.Response_Lock_Prefix + ctx.key
        lock_keys.append(cache_api.exists(lock_key))
        return 'body'

    out = _request(cache_api, channel_item, invoke)

    assert out == 'body'
    assert lock_keys == [False]
    assert response_cache_module.counters.invoke_count == 1

# ################################################################################################################################

def test_response_of_the_earlier_configuration_is_never_served(redis_conn:'Redis') -> 'None':
    """ A request dispatched with the channel item of an earlier configuration, by a worker that has not applied
    the change yet, stores its response under a key that no request of the new configuration reads.
    """
    cache_api = _new_cache_api(redis_conn)

    item_before = _new_channel_item(False, ModuleCtx.Coalesce_Timeout, 'service.before')
    item_after = _new_channel_item(False, ModuleCtx.Coalesce_Timeout, 'service.after')

    # A worker that applied the change purges the key space of the channel ..
    response_cache_module.purge_channel(cache_api, ModuleCtx.Channel_ID)

    # .. a worker that has not applied it yet dispatches a request with the earlier item, which looks the key up
    # after the purge and stores its response ..
    ctx_before = _new_context(cache_api, item_before)
    assert response_cache_module.lookup(ctx_before) is None
    _ = _store_body(ctx_before, 'configuration-before')

    # .. and a request dispatched with the new item is not served it.
    ctx_after = _new_context(cache_api, item_after)
    assert response_cache_module.lookup(ctx_after) is None

    # The response is stored all the same, for the requests of the earlier configuration
    ctx_again = _new_context(cache_api, item_before)
    assert response_cache_module.lookup(ctx_again) == 'configuration-before'

# ################################################################################################################################

def test_response_computed_before_a_purge_is_never_stored(redis_conn:'Redis') -> 'None':
    """ A response whose service ran before purge_channel, which a configuration change runs, is not stored after it.
    """
    cache_api = _new_cache_api(redis_conn)
    channel_item = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)

    ctx_before = _new_context(cache_api, channel_item)
    assert response_cache_module.lookup(ctx_before) is None

    response_cache_module.purge_channel(cache_api, ModuleCtx.Channel_ID)
    _ = _store_body(ctx_before, 'computed-before')

    ctx_after = _new_context(cache_api, channel_item)
    assert response_cache_module.lookup(ctx_after) is None

# ################################################################################################################################

def test_response_computed_before_an_invalidation_is_never_stored(redis_conn:'Redis') -> 'None':
    """ A response whose service read the data before invalidate_response, with or without a pattern,
    is not stored after it returned, while a response computed after it is.
    """
    cache_api = _new_cache_api(redis_conn)
    channel_item = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)

    for pattern in ('', '/api/*'):

        ctx_before = _new_context(cache_api, channel_item)
        assert response_cache_module.lookup(ctx_before) is None

        cache_api.invalidate_response(ModuleCtx.Channel_Name, pattern)
        _ = _store_body(ctx_before, 'data-before')

        ctx_after = _new_context(cache_api, channel_item)
        assert response_cache_module.lookup(ctx_after) is None

        _ = _store_body(ctx_after, 'data-after')

        ctx_next = _new_context(cache_api, channel_item)
        assert response_cache_module.lookup(ctx_next) == 'data-after'

        cache_api.invalidate_response(ModuleCtx.Channel_Name)

# ################################################################################################################################

def test_no_cache_request_stores_under_the_generation_it_read(redis_conn:'Redis') -> 'None':
    """ A request with Cache-Control no-cache skips the lookup and its response is still subject to the generation.
    """
    cache_api = _new_cache_api(redis_conn)
    channel_item = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)

    # The generation is past its initial value ..
    response_cache_module.purge_channel(cache_api, ModuleCtx.Channel_ID)

    # .. a request with no-cache stores its response under it ..
    ctx = _new_context(cache_api, channel_item)
    ctx.skip_lookup = True
    assert response_cache_module.lookup(ctx) is None

    _ = _store_body(ctx, 'computed-current')

    ctx_next = _new_context(cache_api, channel_item)
    assert response_cache_module.lookup(ctx_next) == 'computed-current'

    # .. and one whose service ran before a purge does not.
    ctx_before = _new_context(cache_api, channel_item)
    ctx_before.skip_lookup = True
    assert response_cache_module.lookup(ctx_before) is None

    response_cache_module.purge_channel(cache_api, ModuleCtx.Channel_ID)
    _ = _store_body(ctx_before, 'computed-before')

    ctx_after = _new_context(cache_api, channel_item)
    assert response_cache_module.lookup(ctx_after) is None

# ################################################################################################################################

def test_fingerprint_is_the_same_in_every_process(redis_conn:'Redis') -> 'None':
    """ Two channel items built from one configuration share a key, and a changed plain value gives another key.
    """
    cache_api = _new_cache_api(redis_conn)

    item_one = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)
    item_two = _new_channel_item(False, ModuleCtx.Coalesce_Timeout)

    # A request of the second item memoized what requests memoize on an item
    item_two['deprecation_headers'] = {'Deprecation': '@1'}

    item_changed = _new_channel_item(False, ModuleCtx.Coalesce_Timeout, 'service.changed')

    key_one = _new_context(cache_api, item_one).key
    key_two = _new_context(cache_api, item_two).key
    key_changed = _new_context(cache_api, item_changed).key

    assert key_one == key_two
    assert key_one != key_changed

# ################################################################################################################################
# ################################################################################################################################
