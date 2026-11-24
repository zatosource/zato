# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Requests whose services wait do not hold up other requests.

# stdlib
import time
from concurrent.futures import ThreadPoolExecutor
from http.client import OK

# Zato
from channel_definitions import Paths

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient

# ################################################################################################################################
# ################################################################################################################################

_concurrent_requests = 50
_sleep_seconds = 1.0

# How long all the concurrent requests may take together, as a share of the time they would take one after another
_max_elapsed_share = 0.5

# How long the pending request waits for its release at most, in seconds, below the socket timeout of the client
_held_seconds = 20

# The hold key of the pending request
_hold_key = 'cooperative-scheduling'

# How many requests to another service are sent while the pending one waits
_probe_count = 10

# ################################################################################################################################
# ################################################################################################################################

def test_concurrent_sleeping_requests(client:'ChannelClient') -> 'None':
    path = f'{Paths.Sleep}?seconds={_sleep_seconds}'

    start = time.monotonic()

    with ThreadPoolExecutor(max_workers=_concurrent_requests) as executor:
        futures = []
        for _ in range(_concurrent_requests):
            futures.append(executor.submit(client.get, path))

        statuses = []
        for future in futures:
            statuses.append(future.result().status)

    elapsed = time.monotonic() - start
    serial_elapsed = _concurrent_requests * _sleep_seconds

    assert statuses == [OK] * _concurrent_requests
    assert elapsed < serial_elapsed * _max_elapsed_share, elapsed

# ################################################################################################################################

def test_other_requests_served_during_pending_one(client:'ChannelClient') -> 'None':

    # The pending request waits until it is released ..
    path = f'{Paths.Sleep}?seconds={_held_seconds}&hold={_hold_key}'
    release_path = f'{Paths.Sleep_Release}?hold={_hold_key}'

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(client.get, path)

        # .. each of the other requests is served while it is still pending ..
        for _ in range(_probe_count):
            response = client.get(Paths.Items_Special)

            assert response.status == OK
            assert not future.done()

        # .. and it completes once released.
        response = client.get(release_path)

        assert response.status == OK
        assert future.result().status == OK

# ################################################################################################################################
# ################################################################################################################################
