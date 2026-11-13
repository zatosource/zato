# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Exceptions raised by services and how they are answered and logged.

# stdlib
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, NOT_FOUND, UNAUTHORIZED

# Zato
from channel_definitions import Paths
from channel_suite import assert_json_error, wait_for_log_lines

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient
    from channel_suite import Suite

# ################################################################################################################################
# ################################################################################################################################

_database_message = 'Customer database is unavailable'

# ################################################################################################################################
# ################################################################################################################################

def test_exception(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Error_Exception)

    assert response.reason == 'Internal Server Error'
    _ = assert_json_error(response, INTERNAL_SERVER_ERROR, [_database_message])

# ################################################################################################################################

def test_bad_request(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Error_Bad_Request)
    _ = assert_json_error(response, BAD_REQUEST, 'Bad request')

# ################################################################################################################################

def test_unauthorized(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Error_Unauthorized)

    _ = assert_json_error(response, UNAUTHORIZED, 'Customer token expired')
    assert response.get_header_values('WWW-Authenticate') == ['Bearer']

# ################################################################################################################################

def test_forbidden(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Error_Forbidden)

    _ = assert_json_error(response, FORBIDDEN, 'Customer account is locked')
    assert response.get_header_values('WWW-Authenticate') == []

# ################################################################################################################################

def test_not_found(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Error_Not_Found)
    _ = assert_json_error(response, NOT_FOUND, 'Customer not found')

# ################################################################################################################################

def test_headers_set_before_exception(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Error_After_Headers)

    _ = assert_json_error(response, INTERNAL_SERVER_ERROR, [_database_message])
    assert response.get_header_values('X-Customer-ID') == ['123']

# ################################################################################################################################

def test_error_cid_is_request_cid(client:'ChannelClient') -> 'None':
    first = client.get(Paths.Error_Exception).json()
    second = client.get(Paths.Error_Exception).json()

    assert first['cid'] != second['cid']

# ################################################################################################################################

def test_error_logged(suite:'Suite') -> 'None':
    response = suite.client.get(Paths.Error_Exception)
    cid = response.json()['cid']

    server_log = suite.environment.get_log_path('server.log')
    lines = wait_for_log_lines(server_log, f'Caught an exception, cid:`{cid}`')
    line = lines[0]

    assert ' - INFO - ' in line
    assert ' - test.channel.error.exception - ' in line
    assert 'status_code:`500`' in line
    assert line.endswith('`Traceback (most recent call last):')

# ################################################################################################################################
# ################################################################################################################################
