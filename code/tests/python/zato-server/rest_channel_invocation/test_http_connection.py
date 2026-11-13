# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How the server treats connections and the framing of requests.

# stdlib
from http.client import OK

# Zato
from channel_client import basic_auth_header, build_request
from channel_definitions import Credentials, Paths

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient

# ################################################################################################################################
# ################################################################################################################################

_requests_per_connection = 5

# ################################################################################################################################
# ################################################################################################################################

def test_keep_alive(client:'ChannelClient') -> 'None':
    connection = client.connect()
    cid_list = []

    try:
        for _ in range(_requests_per_connection):
            request = build_request('GET', Paths.Echo, needs_close=False)
            response = connection.exchange(request)

            assert response.status == OK
            assert response.headers['connection'] == 'keep-alive'
            cid_list.append(response.json()['cid'])

        assert not connection.is_closed_by_server()

    finally:
        connection.close()

    assert len(set(cid_list)) == _requests_per_connection

# ################################################################################################################################

def test_connection_close(client:'ChannelClient') -> 'None':
    connection = client.connect()

    try:
        response = connection.exchange(build_request('GET', Paths.Echo, needs_close=True))

        assert response.status == OK
        assert response.headers['connection'] == 'close'
        assert connection.is_closed_by_server()

    finally:
        connection.close()

# ################################################################################################################################

def test_http_10(client:'ChannelClient') -> 'None':
    connection = client.connect()

    try:
        request = build_request('GET', Paths.Echo, http_version='HTTP/1.0', needs_close=False)
        response = connection.exchange(request)

        assert response.status == OK
        assert response.json()['context']['SERVER_PROTOCOL']['value'] == 'HTTP/1.0'
        assert connection.is_closed_by_server()

    finally:
        connection.close()

# ################################################################################################################################

def _assert_closed_without_response(client:'ChannelClient', request:'bytes') -> 'None':
    """ Asserts that the server closes the connection of a request without sending anything back.
    """
    connection = client.connect()

    try:
        connection.send(request)
        received = connection.read_until_closed()
    finally:
        connection.close()

    assert received == b''

# ################################################################################################################################

def test_transfer_encoding_rejected(client:'ChannelClient') -> 'None':
    body = b'5\r\nhello\r\n0\r\n\r\n'
    headers = {'Content-Type': 'application/json', 'Transfer-Encoding': 'chunked'}

    request = build_request('POST', Paths.Echo, headers=headers, body=body, needs_content_length=False)
    _assert_closed_without_response(client, request)

# ################################################################################################################################

def test_duplicate_content_length_rejected(client:'ChannelClient') -> 'None':
    body = b'{"customer_id": 1}'
    content_length = f'Content-Length: {len(body)}\r\n'
    head = f'POST {Paths.Echo} HTTP/1.1\r\nHost: 127.0.0.1\r\n{content_length}{content_length}Connection: close\r\n\r\n'

    _assert_closed_without_response(client, head.encode('ascii') + body)

# ################################################################################################################################

def test_duplicate_authorization_rejected(client:'ChannelClient') -> 'None':
    valid = basic_auth_header(Credentials.Basic_Username, Credentials.Basic_Password)
    other = basic_auth_header(Credentials.Group_Extra_Username, Credentials.Group_Extra_Password)

    authorization = f'Authorization: {valid}\r\nAuthorization: {other}\r\n'
    head = f'GET {Paths.Basic} HTTP/1.1\r\nHost: 127.0.0.1\r\n{authorization}Connection: close\r\n\r\n'

    _assert_closed_without_response(client, head.encode('ascii'))

# ################################################################################################################################

def test_single_authorization_accepted(client:'ChannelClient') -> 'None':
    valid = basic_auth_header(Credentials.Basic_Username, Credentials.Basic_Password)
    head = f'GET {Paths.Basic} HTTP/1.1\r\nHost: 127.0.0.1\r\nAuthorization: {valid}\r\nConnection: close\r\n\r\n'

    response = client.send_raw(head.encode('ascii'))
    assert response.status == OK

# ################################################################################################################################
# ################################################################################################################################
