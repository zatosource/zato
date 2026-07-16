# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from concurrent.futures import ThreadPoolExecutor
from http.client import NOT_MODIFIED, OK

# Requests
import requests

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Timeout for HTTP requests to the server under test, in seconds
_http_timeout = 30

# How many concurrent requests the coalescing test fires
_burst_size = 50

# ################################################################################################################################
# ################################################################################################################################

def _get(url:'str', **kwargs:'any_') -> 'any_':
    out = requests.get(url, timeout=_http_timeout, **kwargs)
    return out

# ################################################################################################################################

def _reset(zato_server:'stranydict') -> 'None':
    """ Resets the invocation and coalescing counters inside the server process.
    """
    response = _get(zato_server['reset_url'])
    assert response.status_code == OK, response.text

# ################################################################################################################################

def _get_count(zato_server:'stranydict') -> 'int':
    """ Returns how many times the data service ran inside the server process.
    """
    response = _get(zato_server['count_url'])
    assert response.status_code == OK, response.text

    out = response.json()['count']
    return out

# ################################################################################################################################

def _get_stats(zato_server:'stranydict') -> 'stranydict':
    """ Returns the first-class coalescing counters of the server process.
    """
    response = _get(zato_server['stats_url'])
    assert response.status_code == OK, response.text

    out = response.json()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_coalescing_and_invalidation(zato_server:'stranydict') -> 'None':

    data_url = zato_server['data_url']

    # A clean slate - the cache may hold entries from previous runs of this module
    response = _get(zato_server['invalidate_url'])
    assert response.status_code == OK, response.text

    # The priming request is a miss that stores the admission marker
    response = _get(data_url)
    assert response.status_code == OK, response.text
    assert response.headers['X-Cache'] == 'Miss'

    # Everything the burst measures starts from zero
    _reset(zato_server)

    # 50 concurrent requests to the one URL of an admitted key
    futures:'anylist' = []
    responses:'anylist' = []

    with ThreadPoolExecutor(max_workers=_burst_size) as executor:

        for _ in range(_burst_size):
            futures.append(executor.submit(_get, data_url))

        for future in futures:
            responses.append(future.result())

    # All the responses are identical and 200
    bodies = set()
    status_codes = set()

    for response in responses:
        bodies.add(response.text)
        status_codes.add(response.status_code)

    assert status_codes == {OK}, status_codes
    assert len(bodies) == 1, bodies

    # The service ran exactly once - one holder, 49 coalesced waiters
    count = _get_count(zato_server)
    assert count == 1, f'Expected 1 invocation, got {count}'

    # Requests that arrived while the holder was still running were coalesced, the ones
    # that arrived after it stored the entry were plain fast-path hits - the split between
    # the two depends on timing, so only the coalesced side's presence is deterministic.
    stats = _get_stats(zato_server)
    assert stats['invoke_count'] == 1, stats
    assert 1 <= stats['coalesced_count'] <= _burst_size - 1, stats
    assert stats['coalesce_timeout_count'] == 0, stats

    # The holder's response is the one miss, everyone else was served from the cache
    cache_headers:'strlist' = []

    for response in responses:
        cache_headers.append(response.headers['X-Cache'])

    assert cache_headers.count('Miss') == 1, cache_headers
    assert cache_headers.count('Hit') == _burst_size - 1, cache_headers

    # A later request is a plain hit carrying the Age header
    response = _get(data_url)
    assert response.status_code == OK, response.text
    assert response.headers['X-Cache'] == 'Hit'
    assert 'Age' in response.headers, response.headers

    # Programmatic invalidation empties the channel's key space ..
    response = _get(zato_server['invalidate_url'])
    assert response.status_code == OK, response.text

    # .. so the next request is a miss again.
    response = _get(data_url)
    assert response.status_code == OK, response.text
    assert response.headers['X-Cache'] == 'Miss'

# ################################################################################################################################

def test_etag_flow(zato_server:'stranydict') -> 'None':

    etag_url = zato_server['etag_url']

    # The channel stores on first miss, so the second request is a hit with an ETag
    response = _get(etag_url)
    assert response.status_code == OK, response.text
    assert response.headers['X-Cache'] == 'Miss'

    response = _get(etag_url)
    assert response.status_code == OK, response.text
    assert response.headers['X-Cache'] == 'Hit'

    etag = response.headers['ETag']
    assert etag, response.headers

    # A matching If-None-Match short-circuits to a bodyless 304
    response = _get(etag_url, headers={'If-None-Match': etag})
    assert response.status_code == NOT_MODIFIED, response.text
    assert response.text == '', response.text

    # A stale ETag still gets the full body
    response = _get(etag_url, headers={'If-None-Match': '"stale"'})
    assert response.status_code == OK, response.text
    assert response.text, response.text

# ################################################################################################################################

def test_no_cache_refresh(zato_server:'stranydict') -> 'None':

    data_url = zato_server['data_url']

    # Make sure the entry is in place - the first two requests admit and store it
    response = _get(data_url)
    assert response.status_code == OK, response.text

    response = _get(data_url)
    assert response.status_code == OK, response.text

    response = _get(data_url)
    assert response.status_code == OK, response.text
    assert response.headers['X-Cache'] == 'Hit'

    # A no-cache request bypasses the lookup and reaches the service
    _reset(zato_server)

    response = _get(data_url, headers={'Cache-Control': 'no-cache'})
    assert response.status_code == OK, response.text
    assert response.headers['X-Cache'] == 'Miss'

    count = _get_count(zato_server)
    assert count == 1, f'Expected the no-cache request to reach the service, got {count} invocations'

# ################################################################################################################################
# ################################################################################################################################
