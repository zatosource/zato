# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a service observes of the HTTP request that invoked it.

# stdlib
import re
from datetime import datetime, timedelta, timezone
from http.client import OK

# Zato
from channel_client import basic_auth_header
from channel_definitions import Channels, Credentials, Paths, Security, Services

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_cid_pattern = re.compile(r'^\d{8}-\d{6}-\d{4}-[0-9a-f]+$')

# How far the request timestamps may be from the clock of the test
_timestamp_tolerance = timedelta(seconds=30)

# ################################################################################################################################
# ################################################################################################################################

def _echo(client:'ChannelClient', path:'str', headers:'anydict | None' = None) -> 'anydict':
    response = client.get(path, headers)
    assert response.status == OK, response.body

    out = response.json()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_method_and_path(client:'ChannelClient') -> 'None':

    for method in ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'):
        response = client.request(method, Paths.Echo)
        data = response.json()

        assert data['method'] == method
        assert data['path'] == Paths.Echo
        assert data['http_to_dict']['method'] == method
        assert data['http_to_dict']['path'] == Paths.Echo

# ################################################################################################################################

def test_headers(client:'ChannelClient') -> 'None':
    headers = {
        'X-Customer-Region': 'North America',
        'X_Underscore_Header': 'underscore',
        'User-Agent': 'CustomerPortal/2.1',
        'Content-Type': 'application/json',
        'X-Repeated': 'first',
    }
    data = _echo(client, Paths.Echo, headers)

    assert data['headers']['x-customer-region'] == 'North America'
    assert data['headers']['host'] == '127.0.0.1'
    assert data['headers']['user-agent'] == 'CustomerPortal/2.1'
    assert 'content-type' not in data['headers']
    assert data['user_agent'] == 'CustomerPortal/2.1'
    assert data['http_to_dict']['headers'] == data['headers']

# ################################################################################################################################

def test_user_agent_absent(client:'ChannelClient') -> 'None':
    data = _echo(client, Paths.Echo)
    assert data['user_agent'] is None

# ################################################################################################################################

def test_query_string(client:'ChannelClient') -> 'None':
    data = _echo(client, Paths.Echo + '?name=J%C3%BCrgen&tag=retail&tag=priority&empty=&flag&plus=John+Smith')

    expected = {
        'name': 'Jürgen',
        'tag': ['retail', 'priority'],
        'empty': '',
        'flag': '',
        'plus': 'John Smith',
    }

    assert data['GET'] == expected
    assert data['params'] == expected
    assert data['POST'] == {}
    assert data['context']['QUERY_STRING']['value'] == 'name=J%C3%BCrgen&tag=retail&tag=priority&empty=&flag&plus=John+Smith'

# ################################################################################################################################

def test_path_parameters_over_query_string(client:'ChannelClient') -> 'None':
    data = _echo(client, '/test/channel/priority/path/1?customer_id=2&segment=retail')

    assert data['params'] == {'customer_id': '1'}
    assert data['GET'] == {'customer_id': '2', 'segment': 'retail'}
    assert data['channel_params'] == {'customer_id': '1', 'segment': 'retail'}
    assert data['input']['value'] == {
        'customer_id': {'type': 'str', 'value': '1'},
        'segment': {'type': 'str', 'value': 'retail'},
    }

# ################################################################################################################################

def test_query_string_over_path_parameters(client:'ChannelClient') -> 'None':
    data = _echo(client, '/test/channel/priority/query/1?customer_id=2&segment=retail')

    assert data['params'] == {'customer_id': '2', 'segment': 'retail'}
    assert data['GET'] == {'customer_id': '2', 'segment': 'retail'}
    assert data['channel_params'] == {'customer_id': '2', 'segment': 'retail'}
    assert data['input']['value'] == {
        'customer_id': {'type': 'str', 'value': '2'},
        'segment': {'type': 'str', 'value': 'retail'},
    }

# ################################################################################################################################

def test_parameters_not_merged(client:'ChannelClient') -> 'None':
    data = _echo(client, '/test/channel/not-merged/1?customer_id=2&segment=retail')

    assert data['params'] == {'customer_id': '1'}
    assert data['GET'] == {}
    assert data['channel_params'] == {}
    assert data['input']['value'] == {}

# ################################################################################################################################

def test_remote_address(client:'ChannelClient') -> 'None':

    # Without forwarding headers, the address is the peer's ..
    data = _echo(client, Paths.Echo)
    assert data['context']['zato.http.remote_addr']['value'] == '127.0.0.1'
    assert data['context']['REMOTE_ADDR']['value'] == '127.0.0.1'

    # .. the address a front proxy forwards is preferred ..
    data = _echo(client, Paths.Echo, {'X-Forwarded-For': '203.0.113.10'})
    assert data['context']['zato.http.remote_addr']['value'] == '203.0.113.10'
    assert data['context']['REMOTE_ADDR']['value'] == '127.0.0.1'

    # .. and the Zato-specific header comes first of all.
    data = _echo(client, Paths.Echo, {'X-Forwarded-For': '203.0.113.10', 'X-Zato-Forwarded-For': '198.51.100.20'})
    assert data['context']['zato.http.remote_addr']['value'] == '198.51.100.20'

# ################################################################################################################################

def test_cid(client:'ChannelClient') -> 'None':
    first = _echo(client, Paths.Echo)
    second = _echo(client, Paths.Echo)

    assert _cid_pattern.match(first['cid']), first['cid']
    assert first['cid'] != second['cid']
    assert first['logging_cid'] == first['cid']

# ################################################################################################################################

def test_logging_context(client:'ChannelClient') -> 'None':
    data = _echo(client, Paths.Echo)

    assert data['logging_service_name'] == Services.Echo
    assert data['service_name'] == Services.Echo

# ################################################################################################################################

def test_channel_without_security(client:'ChannelClient') -> 'None':
    data = _echo(client, Paths.Echo)
    channel = data['channel']

    assert channel['name'] == Channels.Echo
    assert channel['type'] == 'http-soap'
    assert channel['data_format'] == 'json'
    assert channel['is_internal'] is False
    assert channel['security'] == {'id': None, 'name': None, 'type': None, 'username': None}
    assert data['chan'] == channel
    assert data['channel_type'] == 'http-soap'
    assert data['data_format'] == 'json'
    assert data['transport'] == 'plain_http'

# ################################################################################################################################

def test_channel_with_security(client:'ChannelClient') -> 'None':
    authorization = basic_auth_header(Credentials.Basic_Username, Credentials.Basic_Password)
    data = _echo(client, Paths.Basic, {'Authorization': authorization})
    security = data['channel']['security']

    assert data['channel']['name'] == Channels.Basic
    assert security['name'] == Security.Basic
    assert security['type'] == 'basic_auth'
    assert security['username'] == Credentials.Basic_Username
    assert isinstance(security['id'], int)

# ################################################################################################################################

def test_request_timestamps(client:'ChannelClient') -> 'None':
    data = _echo(client, Paths.Echo)
    now = datetime.now(timezone.utc)

    timestamp_utc = datetime.fromisoformat(data['request_timestamp_utc'])
    timestamp_local = datetime.fromisoformat(data['request_timestamp'])

    assert timestamp_utc.utcoffset() == timedelta(0)
    assert abs(now - timestamp_utc) < _timestamp_tolerance
    assert timestamp_local == timestamp_utc

# ################################################################################################################################

def test_request_context_keys(client:'ChannelClient') -> 'None':
    data = _echo(client, Paths.Echo + '?customer_id=1')
    context = data['context']

    assert context['PATH_INFO']['value'] == Paths.Echo
    assert context['RAW_URI']['value'] == Paths.Echo + '?customer_id=1'
    assert context['REQUEST_METHOD']['value'] == 'GET'
    assert context['SERVER_PROTOCOL']['value'] == 'HTTP/1.1'

    for key in ('zato.channel_item', 'zato.http.GET', 'zato.http.POST', 'zato.http.path_params', 'zato.http.raw_request',
            'zato.request_timestamp', 'zato.request_timestamp_utc', 'zato.http.response.headers'):
        assert key in data['context_keys'], key

# ################################################################################################################################
# ################################################################################################################################
