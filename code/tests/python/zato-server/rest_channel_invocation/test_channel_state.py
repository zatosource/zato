# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Inactive and deprecated channels.

# stdlib
import re
import time
from http.client import NOT_FOUND, OK

# Zato
from channel_definitions import Deprecation, Paths
from channel_suite import assert_json_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient

# ################################################################################################################################
# ################################################################################################################################

_deprecation_pattern = re.compile(r'^@(\d+)$')

# How long before the test the deprecation of the channel may have been recorded, in seconds
_max_deprecation_age = 3600

_sunset = 'Wed, 30 Jun 2027 00:00:00 GMT'

# ################################################################################################################################
# ################################################################################################################################

def test_inactive_channel(client:'ChannelClient') -> 'None':

    for method in ('GET', 'POST', 'DELETE'):
        response = client.request(method, Paths.Inactive)
        _ = assert_json_error(response, NOT_FOUND, 'Channel inactive')

# ################################################################################################################################

def test_deprecated_channel(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Deprecated)

    assert response.status == OK
    assert response.json()['path'] == Paths.Deprecated

    deprecation = response.get_header_values('Deprecation')
    assert len(deprecation) == 1

    match = _deprecation_pattern.match(deprecation[0])
    assert match, deprecation

    deprecated_at = int(match.group(1))
    now = time.time()
    assert now - _max_deprecation_age < deprecated_at <= now

    assert response.get_header_values('Sunset') == [_sunset]
    assert response.get_header_values('Link') == [f'<{Deprecation.Successor}>; rel="successor-version"']

# ################################################################################################################################

def test_channel_not_deprecated(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Echo)

    for name in ('Deprecation', 'Sunset', 'Link'):
        assert response.get_header_values(name) == []

# ################################################################################################################################
# ################################################################################################################################
