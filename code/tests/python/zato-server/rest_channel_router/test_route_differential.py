# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Requests routed by the REST channel router, with the dispatcher handling those it declines, produce the same
# response bodies, request contexts, log records and service invocations as the same requests dispatched
# by the request dispatcher alone.

# hypothesis
from hypothesis import event, given, HealthCheck, settings, strategies as st

# Zato
from router_compare import compare, pinned_time, snapshot_request_ctx, Test_CID
from router_environment import channel_definitions, Clock, Credentials, declined_channel_definitions, RouterWorld
from router_requests import basic_auth, build_request_ctx, make_request, requests
from zato_server_core.zato_server_core import ChannelRouter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

DISPATCHER = ChannelRouter.DISPATCHER
RESPONSE = ChannelRouter.RESPONSE
INVOKE = ChannelRouter.INVOKE

_start_us = 1_794_571_200_000_000

# The microseconds between two requests of a scenario
_scenario_step_us = 1000

# The microseconds between two generated requests, from none at all to more than a rate limit refill period
_generated_steps_us = st.sampled_from([0, 0, 1000, 600_000, 2_000_000])

# ################################################################################################################################
# ################################################################################################################################

_basic = basic_auth(Credentials.Basic_Username, Credentials.Basic_Password)
_basic_wrong = basic_auth(Credentials.Basic_Username, 'password.wrong')
_limited = basic_auth(Credentials.Limited_Username, Credentials.Limited_Password)

_scenarios = [
    (make_request('GET', '/api/customer/123'), INVOKE),
    (make_request('GET', '/api/customer/123', query='name=John%20Smith', user_agent='Agent\u0007'), INVOKE),
    (make_request('GET', '/api/customer/John Smith', remote_addr='10.0.0.5'), INVOKE),
    (make_request('GET', '/api/customer/a/b'), RESPONSE),
    (make_request('DELETE', '/api/customer/123'), RESPONSE),
    (make_request('POST', '/api/customer/123', accept='application/json', body=b'{"name": "John Smith"}'), INVOKE),
    (make_request('POST', '/api/customer/123', accept='text/plain'), RESPONSE),
    (make_request('PUT', '/api/any/a/b/c'), INVOKE),
    (make_request('GET', '/api/orders'), INVOKE),
    (make_request('GET', '/api/orders/'), INVOKE),
    (make_request('GET', '/api/./orders'), INVOKE),
    (make_request('GET', '/api/%6Frders'), INVOKE),
    (make_request('DELETE', '/api/orders/1/items/2'), INVOKE),
    (make_request('DELETE', '/api/orders/1/items/a/b'), INVOKE),
    (make_request('TRACE', '/api/orders'), RESPONSE),
    (make_request('OPTIONS', '/api/orders', origin='http://localhost:8080'), RESPONSE),
    (make_request('GET', '/api/orders', origin='https://zato.io'), INVOKE),
    (make_request('GET', '/api/orders', origin='https://example.com'), INVOKE),
    (make_request('GET', '/api/ignored'), INVOKE),
    (make_request('GET', '/api/unknown'), RESPONSE),
    (make_request('GET', '/api/zato/ping'), RESPONSE),
    (make_request('GET', '/api/basic', authorization=_basic), INVOKE),
    (make_request('GET', '/api/basic', authorization=_basic_wrong), DISPATCHER),
    (make_request('GET', '/api/basic'), DISPATCHER),
    (make_request('GET', '/api/apikey', api_key=Credentials.API_Key), INVOKE),
    (make_request('GET', '/api/apikey', api_key='key.wrong'), DISPATCHER),
    (make_request('GET', '/api/bearer', authorization='Bearer ' + Credentials.Static_Token), INVOKE),
    (make_request('GET', '/api/bearer-field', authorization='bearer  ' + Credentials.Field_Token + ' '), INVOKE),
    (make_request('GET', '/api/bearer', authorization='Bearer token.wrong'), DISPATCHER),
    (make_request('GET', '/api/basic-inactive', authorization=_basic), DISPATCHER),
    (make_request('GET', '/api/limited'), INVOKE),
    (make_request('GET', '/api/limited'), INVOKE),
    (make_request('GET', '/api/limited'), RESPONSE),
    (make_request('GET', '/api/disallowed'), RESPONSE),
    (make_request('GET', '/api/sec-limited', authorization=_limited), INVOKE),
    (make_request('GET', '/api/sec-limited', authorization=_limited), INVOKE),
    (make_request('GET', '/api/sec-limited', authorization=_limited), RESPONSE),
    (make_request('GET', '/api/sec-limited-self', authorization=_limited), INVOKE),
    (make_request('GET', '/api/deprecated'), INVOKE),
    (make_request('GET', '/api/deprecated'), INVOKE),
    (make_request('GET', '/api/inactive'), DISPATCHER),
    (make_request('GET', '/zato/ping'), DISPATCHER),
    (make_request('GET', '/api/customer/123', is_portal=True), DISPATCHER),
    (make_request('GET', '/api/customer/123'), INVOKE),
]

# ################################################################################################################################
# ################################################################################################################################

def test_every_channel_is_supported() -> 'None':
    """ The router accepts every channel of the comparison, including those whose requests it declines.
    """
    definitions = channel_definitions() + declined_channel_definitions()
    world = RouterWorld(definitions, Clock(_start_us))

    assert world.router.unsupported_channels() == []
    assert world.router.is_complete()

# ################################################################################################################################

def test_scenarios() -> 'None':
    """ Every path through the router produces what the dispatcher produces for the same request.
    """
    clock = Clock(_start_us)

    dispatcher_world = RouterWorld(channel_definitions(), clock)
    router_world = RouterWorld(channel_definitions(), clock)

    with pinned_time(clock):
        for request, expected_code in _scenarios:
            code = compare(dispatcher_world, router_world, request)
            assert code == expected_code, (request, code)
            clock.advance(_scenario_step_us)

# ################################################################################################################################

def test_declined_channels() -> 'None':
    """ The router hands every request of a channel that needs the dispatcher to it, untouched.
    """
    world = RouterWorld(declined_channel_definitions(), Clock(_start_us))

    paths = {
        '/api/queued': 'POST',
        '/api/cached': 'GET',
        '/api/form': 'POST',
        '/api/hl7': 'POST',
        '/api/soap': 'POST',
        '/api/audited': 'GET',
        '/api/grouped': 'GET',
    }

    for path, method in paths.items():
        request_ctx = build_request_ctx(make_request(method, path))
        pristine = snapshot_request_ctx(request_ctx)

        code, value = world.router.route(Test_CID, request_ctx, 'curl/8.5.0', '127.0.0.1')

        assert code == DISPATCHER, path
        assert value is None
        assert snapshot_request_ctx(request_ctx) == pristine

# ################################################################################################################################

def test_memoized_response_cache() -> 'None':
    """ A channel the dispatcher has memoized the absence of a response cache on is still routed,
    whereas one with a memoized response cache configuration is declined.
    """
    world = RouterWorld(channel_definitions(), Clock(_start_us))

    for item in world.url_data.channel_data:
        if item['name'] == 'order.list':
            item['response_cache_parsed'] = None

    request_ctx = build_request_ctx(make_request('GET', '/api/orders'))
    code, _ = world.router.route(Test_CID, request_ctx, 'curl/8.5.0', '127.0.0.1')
    assert code == INVOKE

    for item in world.url_data.channel_data:
        if item['name'] == 'order.list':
            item['response_cache_parsed'] = object()

    request_ctx = build_request_ctx(make_request('GET', '/api/orders'))
    code, _ = world.router.route(Test_CID, request_ctx, 'curl/8.5.0', '127.0.0.1')
    assert code == DISPATCHER

# ################################################################################################################################

@settings(max_examples=300, deadline=None, suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large])
@given(st.lists(st.tuples(requests, _generated_steps_us), min_size=1, max_size=20))
def test_generated_sequences(sequence:'anylist') -> 'None':
    """ Any sequence of requests produces the same on both sides, including the rate limit state it leaves behind.
    """
    clock = Clock(_start_us)

    dispatcher_world = RouterWorld(channel_definitions(), clock)
    router_world = RouterWorld(channel_definitions(), clock)

    with pinned_time(clock):
        for request, step_us in sequence:
            code = compare(dispatcher_world, router_world, request)
            event(f'Router outcome {code}')
            clock.advance(step_us)

# ################################################################################################################################
# ################################################################################################################################
