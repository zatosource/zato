# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a request path and method select a channel.

# stdlib
import re
from http.client import METHOD_NOT_ALLOWED, NOT_FOUND, OK

# Zato
from channel_definitions import Channels, Paths, Services
from channel_suite import assert_json_error, wait_until

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient, HTTPResponse
    from channel_suite import Suite

# ################################################################################################################################
# ################################################################################################################################

_not_found_pattern = re.compile(r'^URL not found \(CID:[0-9a-f-]+\)$')
_method_not_allowed_pattern = re.compile(r'^Method not allowed \(CID:[0-9a-f-]+\)$')

_ping_response = {'customer_id': 123, 'status': 'active'}

# ################################################################################################################################
# ################################################################################################################################

def _assert_not_found(response:'HTTPResponse') -> 'None':
    """ Asserts that no channel matched the request.
    """
    assert response.status == NOT_FOUND
    assert _not_found_pattern.match(response.text), response.text
    assert 'content-type' not in response.headers

# ################################################################################################################################

def _matched_channel(response:'HTTPResponse') -> 'str':
    """ Returns the name of the channel the echo service was invoked through.
    """
    assert response.status == OK, response.body
    out = response.json()['channel']['name']
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_static_path(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Echo)

    assert _matched_channel(response) == Channels.Echo
    assert response.json()['service_name'] == Services.Echo

# ################################################################################################################################

def test_path_parameters(client:'ChannelClient') -> 'None':
    response = client.get('/test/channel/customers/123/orders/456')
    data = response.json()

    assert _matched_channel(response) == Channels.Customer_Orders
    assert data['params'] == {'customer_id': '123', 'order_id': '456'}
    assert data['path'] == '/test/channel/customers/123/orders/456'

# ################################################################################################################################

def test_path_parameter_across_slashes(client:'ChannelClient') -> 'None':
    response = client.get('/test/channel/files/reports/2026/summary.txt')

    assert _matched_channel(response) == 'test.channel.files'
    assert response.json()['params'] == {'file_path': 'reports/2026/summary.txt'}

# ################################################################################################################################

def test_match_slash_off(client:'ChannelClient') -> 'None':

    # A single segment matches ..
    response = client.get('/test/channel/single-files/summary.txt')
    assert _matched_channel(response) == 'test.channel.single-files'
    assert response.json()['params'] == {'file_name': 'summary.txt'}

    # .. but a parameter does not extend across a slash.
    response = client.get('/test/channel/single-files/reports/summary.txt')
    _assert_not_found(response)

# ################################################################################################################################

def test_trailing_slash(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Echo + '/')
    _assert_not_found(response)

# ################################################################################################################################

def test_path_normalized(client:'ChannelClient') -> 'None':

    for path in ('/test/channel//echo', '/test/channel/./echo', '/test/channel/customers/../echo', '/test/channel/%65cho'):
        response = client.get(path)
        assert _matched_channel(response) == Channels.Echo, path
        assert response.json()['path'] == Paths.Echo

# ################################################################################################################################

def test_percent_encoded_parameters(client:'ChannelClient') -> 'None':
    response = client.get('/test/channel/customers/John%20Smith/orders/A%2F1')
    data = response.json()

    assert _matched_channel(response) == Channels.Customer_Orders
    assert data['params'] == {'customer_id': 'John Smith', 'order_id': 'A%2F1'}
    assert data['path'] == '/test/channel/customers/John Smith/orders/A%2F1'

# ################################################################################################################################

def test_most_specific_channel_wins(client:'ChannelClient') -> 'None':

    response = client.get(Paths.Items_Special)
    assert response.status == OK
    assert response.json() == _ping_response

    response = client.get('/test/channel/items/42')
    assert _matched_channel(response) == 'test.channel.items.generic'
    assert response.json()['params'] == {'item_id': '42'}

# ################################################################################################################################

def test_user_channel_before_internal(client:'ChannelClient') -> 'None':
    response = client.get('/openapi/customers')

    assert response.status == OK
    assert response.json() == _ping_response

# ################################################################################################################################

def test_not_found(client:'ChannelClient') -> 'None':

    for method in ('GET', 'POST', 'DELETE'):
        response = client.request(method, '/test/channel/no-such-path/customer-data')
        _assert_not_found(response)
        assert 'no-such-path' not in response.text

# ################################################################################################################################

def test_method_not_allowed(client:'ChannelClient') -> 'None':

    response = client.get(Paths.Method_GET)
    assert response.status == OK

    for method in ('POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'):
        response = client.request(method, Paths.Method_GET)
        assert response.status == METHOD_NOT_ALLOWED, method
        assert _method_not_allowed_pattern.match(response.text), response.text
        assert response.get_header_values('Allow') == ['GET']

    response = client.request('HEAD', Paths.Method_GET)
    assert response.status == METHOD_NOT_ALLOWED
    assert response.get_header_values('Allow') == ['GET']

# ################################################################################################################################

def test_unsupported_method(client:'ChannelClient') -> 'None':

    for path in (Paths.Echo, Paths.Method_GET, '/test/channel/no-such-path'):
        for method in ('TRACE', 'CONNECT', 'PROPFIND'):
            response = client.request(method, path)
            assert response.status == METHOD_NOT_ALLOWED
            assert response.json()['details'] == 'Unsupported HTTP method'
            assert response.get_header_values('Allow') == []

# ################################################################################################################################

def test_channel_accept_header(client:'ChannelClient') -> 'None':

    response = client.get(Paths.Accept_JSON, {'Accept': 'application/json'})
    assert _matched_channel(response) == 'test.channel.accept'

    response = client.get(Paths.Accept_JSON, {'Accept': 'text/html'})
    _assert_not_found(response)

    response = client.get(Paths.Accept_JSON)
    _assert_not_found(response)

# ################################################################################################################################

def test_accept_header_of_channel_without_one(client:'ChannelClient') -> 'None':

    for accept in ('application/json', 'text/html', 'application/xml'):
        response = client.get(Paths.Echo, {'Accept': accept})
        assert _matched_channel(response) == Channels.Echo

# ################################################################################################################################

def test_channel_lifecycle(suite:'Suite') -> 'None':
    client = suite.client

    try:

        # The channel as created ..
        response = client.get(Paths.Lifecycle)
        assert _matched_channel(response) == Channels.Lifecycle

        # .. its path edited ..
        suite.import_yaml(lifecycle_path=Paths.Lifecycle_Edited)

        def _is_edited() -> 'bool':
            out = client.get(Paths.Lifecycle_Edited).status == OK
            return out

        _ = wait_until(_is_edited)

        _assert_not_found(client.get(Paths.Lifecycle))
        assert _matched_channel(client.get(Paths.Lifecycle_Edited)) == Channels.Lifecycle

        # .. its service changed ..
        suite.import_yaml(lifecycle_path=Paths.Lifecycle_Edited, lifecycle_service=Services.Ping)

        def _is_service_changed() -> 'bool':
            out = client.get(Paths.Lifecycle_Edited).json() == _ping_response
            return out

        _ = wait_until(_is_service_changed)

        # .. and the channel deactivated, which is how enmasse takes a channel out of service.
        suite.import_yaml(lifecycle_path=Paths.Lifecycle_Edited, lifecycle_service=Services.Ping, is_lifecycle_active=False)

        def _is_deactivated() -> 'bool':
            out = client.get(Paths.Lifecycle_Edited).status == NOT_FOUND
            return out

        _ = wait_until(_is_deactivated)

        response = client.get(Paths.Lifecycle_Edited)
        _ = assert_json_error(response, NOT_FOUND, 'Channel inactive')

    finally:
        suite.restore_yaml()

    def _is_restored() -> 'bool':
        out = client.get(Paths.Lifecycle).status == OK
        return out

    _ = wait_until(_is_restored)

# ################################################################################################################################
# ################################################################################################################################
