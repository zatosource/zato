# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Rate limits of channels and of security definitions.

# stdlib
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.client import OK, TOO_MANY_REQUESTS

# Zato
from channel_client import basic_auth_header
from channel_definitions import Credentials, Limits, Paths
from channel_suite import wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient, HTTPResponse
    from channel_suite import Suite
    from zato.common.typing_ import intlist, strdict

# ################################################################################################################################
# ################################################################################################################################

_quota_headers = ('x-ratelimit-limit', 'x-ratelimit-remaining')

# How long a token bucket takes to refill completely, with a margin, in seconds
_refill_wait = 8

# The furthest in the future a Retry-After date may point, in seconds
_max_retry_after = 120

_limited_headers = {'Authorization': basic_auth_header(Credentials.Limited_Username, Credentials.Limited_Password)}

# ################################################################################################################################
# ################################################################################################################################

def _statuses(client:'ChannelClient', path:'str', count:'int', headers:'strdict | None' = None) -> 'intlist':
    """ Sends requests one after another as fast as possible and returns their statuses.
    """
    out:'intlist' = []

    for _ in range(count):
        response = client.get(path, headers)
        out.append(response.status)

    return out

# ################################################################################################################################

def _assert_too_many_requests(response:'HTTPResponse') -> 'None':
    """ Asserts that a request was rate limited, with a JSON body that has no content type of its own
    and a Retry-After date shortly in the future.
    """
    assert response.status == TOO_MANY_REQUESTS, response.body
    assert 'content-type' not in response.headers

    data = response.json()

    assert data['result'] == 'Error'
    assert data['details'] == 'Too many requests'
    assert data['cid']

    retry_after = parsedate_to_datetime(response.headers['retry-after'])
    now = datetime.now(timezone.utc)
    seconds = (retry_after - now).total_seconds()

    assert -1 < seconds < _max_retry_after, response.headers['retry-after']

# ################################################################################################################################

def _wait_for_refill() -> 'None':
    time.sleep(_refill_wait)

# ################################################################################################################################
# ################################################################################################################################

def test_channel_limit(client:'ChannelClient') -> 'None':
    _wait_for_refill()

    # The burst is admitted and the next request is limited ..
    statuses = _statuses(client, Paths.Rate_Channel, Limits.Channel_Burst)
    assert statuses == [OK] * Limits.Channel_Burst

    response = client.get(Paths.Rate_Channel)
    _assert_too_many_requests(response)

    # .. without the quota headers, which only a security definition's limit adds.
    for name in _quota_headers:
        assert name not in response.headers

# ################################################################################################################################

def test_channel_limit_refills(client:'ChannelClient') -> 'None':
    _wait_for_refill()

    statuses = _statuses(client, Paths.Rate_Channel, Limits.Channel_Burst + 1)
    assert statuses[-1] == TOO_MANY_REQUESTS

    _wait_for_refill()
    assert client.get(Paths.Rate_Channel).status == OK

# ################################################################################################################################

def test_security_definition_limit(client:'ChannelClient') -> 'None':
    _wait_for_refill()

    for expected_remaining in range(Limits.Security_Burst - 1, -1, -1):
        response = client.get(Paths.Rate_Security, _limited_headers)

        assert response.status == OK
        assert response.headers['x-ratelimit-limit'] == str(Limits.Security_Burst)
        assert response.headers['x-ratelimit-remaining'] == str(expected_remaining)

    response = client.get(Paths.Rate_Security, _limited_headers)
    _assert_too_many_requests(response)

    assert response.headers['x-ratelimit-limit'] == str(Limits.Security_Burst)
    assert response.headers['x-ratelimit-remaining'] == '0'

# ################################################################################################################################

def test_disallowed_traffic(client:'ChannelClient') -> 'None':

    # The service behind the channel returns a description of its request, so an empty body
    # means that the request never reached it.
    for _ in range(Limits.Channel_Burst + 1):
        response = client.get(Paths.Rate_Disallowed)
        assert response.body == b''

# ################################################################################################################################

def test_limit_changed(suite:'Suite') -> 'None':
    client = suite.client
    _wait_for_refill()

    statuses = _statuses(client, Paths.Rate_Changing, Limits.Changing_First + 1)
    assert statuses == [OK] * Limits.Changing_First + [TOO_MANY_REQUESTS]

    try:
        suite.import_yaml(rate_changing=Limits.Changing_Second)

        # The new burst is in effect once more requests than the old one allowed are admitted in a row
        def _is_changed() -> 'bool':
            _wait_for_refill()
            statuses = _statuses(client, Paths.Rate_Changing, Limits.Changing_First + 1)
            out = statuses == [OK] * (Limits.Changing_First + 1)
            return out

        _ = wait_until(_is_changed, timeout=60)

        _wait_for_refill()
        statuses = _statuses(client, Paths.Rate_Changing, Limits.Changing_Second + 1)
        assert statuses == [OK] * Limits.Changing_Second + [TOO_MANY_REQUESTS]

    finally:
        suite.restore_yaml()

# ################################################################################################################################
# ################################################################################################################################
