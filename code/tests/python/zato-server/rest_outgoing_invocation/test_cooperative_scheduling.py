# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Cooperative scheduling - an invocation waiting for its response yields to other greenlets, so concurrent invocations
# overlap and other greenlets keep running while one is pending.

# stdlib
from http.client import OK
from time import monotonic

# gevent
from gevent import joinall, sleep as gevent_sleep, spawn

# Test support
from endpoint import EndpointResponse
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# How long the endpoint waits before it answers, in seconds
_delay = 0.5

# How many greenlets invoke the connection at the same time
_concurrency = 50

# How often the timer greenlet runs, in seconds
_timer_interval = 0.05

# ################################################################################################################################
# ################################################################################################################################

def test_concurrent_invocations_overlap(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Concurrent invocations of one connection complete in approximately the delay of one response rather than in the sum of all of them.
    """
    endpoint.set_response(path, EndpointResponse(body='Delayed response', delay=_delay))

    connection = new_connection(server, endpoint.http_base, path)

    greenlets = []
    start = monotonic()

    for _ in range(_concurrency):
        greenlet = spawn(connection.get, Test_CID)
        greenlets.append(greenlet)

    _ = joinall(greenlets, raise_error=True)

    elapsed = monotonic() - start

    for greenlet in greenlets:
        response = greenlet.value
        assert response.status_code == OK
        assert response.text == 'Delayed response'

    assert len(endpoint.get_requests(path)) == _concurrency
    assert elapsed < _delay * 5

# ################################################################################################################################

def test_concurrent_tls_invocations_overlap(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ Concurrent invocations over TLS complete in approximately the delay of one response rather than in the sum of all of them.
    """
    endpoint.set_response(path, EndpointResponse(delay=_delay))

    connection = new_connection(server, endpoint.https_base, path, ca_certs_path=endpoint.certificates.ca_path)

    greenlets = []
    start = monotonic()

    for _ in range(_concurrency):
        greenlet = spawn(connection.get, Test_CID)
        greenlets.append(greenlet)

    _ = joinall(greenlets, raise_error=True)

    elapsed = monotonic() - start

    assert len(endpoint.get_requests(path)) == _concurrency
    assert elapsed < _delay * 5

# ################################################################################################################################

def test_timer_runs_during_invocation(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A timer greenlet keeps running while an invocation waits for its response.
    """
    endpoint.set_response(path, EndpointResponse(delay=_delay))

    connection = new_connection(server, endpoint.http_base, path)

    ticks:'list[float]' = []
    is_running = True

    def run_timer() -> 'None':
        while is_running:
            ticks.append(monotonic())
            gevent_sleep(_timer_interval)

    timer = spawn(run_timer)

    _ = connection.get(Test_CID)

    is_running = False
    _ = timer.join()

    # The invocation took the whole delay, during which the timer ran at its interval
    expected_ticks = _delay / _timer_interval
    assert len(ticks) >= expected_ticks / 2

# ################################################################################################################################
# ################################################################################################################################
