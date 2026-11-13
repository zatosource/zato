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

# How long all the concurrent requests may take together, as a multiple of the time one of them sleeps
_max_elapsed_factor = 3

# How often requests to another service are sent while the sleeping ones are pending, in seconds
_probe_interval = 0.1

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

    assert statuses == [OK] * _concurrent_requests
    assert elapsed < _sleep_seconds * _max_elapsed_factor, elapsed

# ################################################################################################################################

def test_other_requests_served_during_pending_one(client:'ChannelClient') -> 'None':
    path = f'{Paths.Sleep}?seconds={_sleep_seconds * 2}'

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(client.get, path)
        time.sleep(_probe_interval)

        latencies = []
        while not future.done():
            start = time.monotonic()
            response = client.get(Paths.Items_Special)
            latencies.append(time.monotonic() - start)

            assert response.status == OK
            time.sleep(_probe_interval)

        assert future.result().status == OK

    assert len(latencies) > 5
    assert max(latencies) < _sleep_seconds

# ################################################################################################################################
# ################################################################################################################################
