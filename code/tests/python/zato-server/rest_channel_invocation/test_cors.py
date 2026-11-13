# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Cross-origin requests - preflights and the headers of actual requests.

# stdlib
from http.client import METHOD_NOT_ALLOWED, NO_CONTENT, NOT_FOUND, OK, UNAUTHORIZED

# Zato
from channel_definitions import Paths

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient, HTTPResponse

# ################################################################################################################################
# ################################################################################################################################

_allowed_origins = ('https://zato.io', 'http://localhost', 'http://localhost:8080', 'http://127.0.0.1', 'http://127.0.0.1:3000')
_disallowed_origins = ('https://customers.example.com', 'http://localhost.example.com', 'https://zato.io.example.com')

_allow_methods = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
_allow_headers = 'X-API-Key, Authorization, Content-Type, Mcp-Session-Id, MCP-Protocol-Version, Mcp-Method, Mcp-Name, Last-Event-ID'
_expose_headers = 'Mcp-Session-Id'
_max_age = '86400'

_cors_header_names = (
    'access-control-allow-origin',
    'access-control-allow-methods',
    'access-control-allow-headers',
    'access-control-expose-headers',
    'access-control-max-age',
)

# ################################################################################################################################
# ################################################################################################################################

def _preflight(client:'ChannelClient', path:'str', origin:'str') -> 'HTTPResponse':
    headers = {
        'Origin': origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type, Authorization',
    }
    out = client.request('OPTIONS', path, headers=headers)
    return out

# ################################################################################################################################

def _assert_no_cors_headers(response:'HTTPResponse') -> 'None':
    for name in _cors_header_names:
        assert name not in response.headers, name

# ################################################################################################################################
# ################################################################################################################################

def test_preflight_from_allowed_origin(client:'ChannelClient') -> 'None':

    # The preflight is answered before authentication and before URL matching
    for path in (Paths.Echo, Paths.Basic, '/test/channel/no-such-path'):
        for origin in _allowed_origins:
            response = _preflight(client, path, origin)

            assert response.status == NO_CONTENT, (path, origin)
            assert response.body == b''
            assert response.headers['access-control-allow-origin'] == origin
            assert response.headers['access-control-allow-methods'] == _allow_methods
            assert response.headers['access-control-allow-headers'] == _allow_headers
            assert response.headers['access-control-max-age'] == _max_age
            assert 'access-control-expose-headers' not in response.headers

# ################################################################################################################################

def test_preflight_from_disallowed_origin(client:'ChannelClient') -> 'None':

    for origin in _disallowed_origins:

        # The request goes to the channel as any other OPTIONS request ..
        response = _preflight(client, Paths.Echo, origin)
        assert response.status == OK
        assert response.json()['method'] == 'OPTIONS'
        _assert_no_cors_headers(response)

        # .. so a secured channel rejects it ..
        response = _preflight(client, Paths.Basic, origin)
        assert response.status == UNAUTHORIZED
        _assert_no_cors_headers(response)

        # .. and a path no channel serves is not found.
        response = _preflight(client, '/test/channel/no-such-path', origin)
        assert response.status == NOT_FOUND
        _assert_no_cors_headers(response)

# ################################################################################################################################

def test_actual_request_from_allowed_origin(client:'ChannelClient') -> 'None':

    for origin in _allowed_origins:
        response = client.get(Paths.Echo, {'Origin': origin})

        assert response.status == OK
        assert response.headers['access-control-allow-origin'] == origin
        assert response.headers['access-control-expose-headers'] == _expose_headers
        assert 'access-control-allow-methods' not in response.headers
        assert response.json()['headers']['origin'] == origin

# ################################################################################################################################

def test_error_responses_from_allowed_origin(client:'ChannelClient') -> 'None':
    origin = _allowed_origins[0]

    response = client.get(Paths.Basic, {'Origin': origin})
    assert response.status == UNAUTHORIZED
    assert response.headers['access-control-allow-origin'] == origin
    assert response.headers['access-control-expose-headers'] == _expose_headers

    response = client.request('TRACE', Paths.Echo, headers={'Origin': origin})
    assert response.status == METHOD_NOT_ALLOWED
    assert response.headers['access-control-allow-origin'] == origin

# ################################################################################################################################

def test_actual_request_from_disallowed_origin(client:'ChannelClient') -> 'None':

    for origin in _disallowed_origins:
        response = client.get(Paths.Echo, {'Origin': origin})
        assert response.status == OK
        _assert_no_cors_headers(response)

# ################################################################################################################################

def test_request_without_origin(client:'ChannelClient') -> 'None':

    response = client.get(Paths.Echo)
    assert response.status == OK
    _assert_no_cors_headers(response)

    response = client.request('OPTIONS', Paths.Echo)
    assert response.status == OK
    assert response.json()['method'] == 'OPTIONS'
    _assert_no_cors_headers(response)

# ################################################################################################################################
# ################################################################################################################################
