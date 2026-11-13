# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Channels whose responses are cached and channels that put requests on a queue instead of invoking their services.

# stdlib
from http.client import OK

# Zato
from channel_definitions import Paths, Queue_Static_Response

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient

# ################################################################################################################################
# ################################################################################################################################

def test_cached_response(client:'ChannelClient') -> 'None':
    path = Paths.Cached + '?customer_id=cached-response'

    first = client.get(path)
    second = client.get(path)

    assert first.status == OK
    assert second.status == OK

    # The echo service reports the CID of its request, so the same body means the second response came from the cache
    assert second.body == first.body
    assert second.headers['content-type'] == first.headers['content-type']

# ################################################################################################################################

def test_cache_key_includes_query_string(client:'ChannelClient') -> 'None':
    first = client.get(Paths.Cached + '?customer_id=first-key')
    second = client.get(Paths.Cached + '?customer_id=second-key')

    assert first.json()['cid'] != second.json()['cid']
    assert second.json()['GET'] == {'customer_id': 'second-key'}

# ################################################################################################################################

def test_channel_without_cache(client:'ChannelClient') -> 'None':
    first = client.get(Paths.Echo + '?customer_id=not-cached')
    second = client.get(Paths.Echo + '?customer_id=not-cached')

    assert first.json()['cid'] != second.json()['cid']

# ################################################################################################################################

def test_queue_channel_acknowledgement(client:'ChannelClient') -> 'None':
    response = client.post_json(Paths.Queue, {'customer_id': 123})

    assert response.status == OK
    data = response.json()

    assert data['is_ok'] is True
    assert data['cid']
    assert 'service_name' not in data

# ################################################################################################################################

def test_queue_channel_static_response(client:'ChannelClient') -> 'None':
    response = client.post_json(Paths.Queue_Static, {'customer_id': 123})

    assert response.status == OK
    assert response.text == Queue_Static_Response

# ################################################################################################################################
# ################################################################################################################################
