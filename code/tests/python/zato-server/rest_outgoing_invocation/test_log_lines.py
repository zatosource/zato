# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Log lines - the line written before a request is sent and the line written for each response received,
# with the fields that describe the call.

# stdlib
import re
from http.client import INTERNAL_SERVER_ERROR, OK, TOO_MANY_REQUESTS
from json import dumps

# pytest
import pytest

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.exception import BackendInvocationError
from zato.common.util import http_retry

# Test support
from endpoint import CloseMode, EndpointResponse
from support import Basic_Password, Basic_Username, new_connection, read_log_lines, Token_Path_Suffix

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The level every line is written with
_info = ' - INFO - '

# What the elapsed time of a response looks like in a line
_elapsed_pattern = r'\d+:\d\d:\d\d(\.\d+)?'

# ################################################################################################################################
# ################################################################################################################################

def _get_cid(path:'str') -> 'str':
    """ Returns a correlation ID unique to the test, so the lines of one test are told apart from those of any other.
    """
    suffix = path.rsplit('/', 1)[1]

    out = f'zrest-log-{suffix}'
    return out

# ################################################################################################################################

def _get_request_lines(log_path:'str', cid:'str') -> 'list[str]':
    out = read_log_lines(log_path, f'REST out -> cid={cid};')
    return out

# ################################################################################################################################

def _get_response_lines(log_path:'str', cid:'str') -> 'list[str]':
    out = read_log_lines(log_path, f'REST out ← cid={cid};')
    return out

# ################################################################################################################################

def _assert_response_line(line:'str', cid:'str', status:'int', length:'int') -> 'None':
    pattern = rf'REST out ← cid={cid}; {status} time={_elapsed_pattern}; len={length}$'

    assert _info in line
    assert re.search(pattern, line), line

# ################################################################################################################################
# ################################################################################################################################

def test_lines_without_security(endpoint:'TestEndpoint', server:'ServerStub', path:'str', rest_log_path:'str') -> 'None':
    """ A call of a connection without security writes a request line with an empty security definition and a response line.
    """
    cid = _get_cid(path)
    endpoint.set_response(path, EndpointResponse(body='Response body'))

    connection = new_connection(server, endpoint.http_base, path)
    _ = connection.get(cid)

    request_line, = _get_request_lines(rest_log_path, cid)
    response_line, = _get_response_lines(rest_log_path, cid)

    address = endpoint.http_base + path

    assert _info in request_line
    assert request_line.endswith(f'REST out -> cid={cid}; GET {address}; name:test.rest.outgoing; len=0; sec= ()')

    _assert_response_line(response_line, cid, OK, len('Response body'))

# ################################################################################################################################

def test_lines_with_basic_auth(endpoint:'TestEndpoint', server:'ServerStub', path:'str', rest_log_path:'str') -> 'None':
    """ A call with a body of a connection with Basic Auth writes the body length and the security definition with its type.
    """
    cid = _get_cid(path)
    endpoint.set_response(path, EndpointResponse(INTERNAL_SERVER_ERROR, 'Internal error'))

    connection = new_connection(
        server,
        endpoint.http_base,
        path,
        name='test.log.basic.auth',
        sec_type=SEC_DEF_TYPE.BASIC_AUTH,
        security_name='test.basic.auth',
        username=Basic_Username,
        password=Basic_Password,
    )

    _ = connection.post(cid, 'Zürich request body', {'page': 2})

    request_line, = _get_request_lines(rest_log_path, cid)
    response_line, = _get_response_lines(rest_log_path, cid)

    address = endpoint.http_base + path
    body_length = len('Zürich request body'.encode('utf8'))

    expected = f'REST out -> cid={cid}; POST {address}; name:test.log.basic.auth; len={body_length}; ' + \
        f'sec=test.basic.auth ({SEC_DEF_TYPE.BASIC_AUTH})'

    assert request_line.endswith(expected)
    _assert_response_line(response_line, cid, INTERNAL_SERVER_ERROR, len('Internal error'))

# ################################################################################################################################

def test_lines_with_static_token(endpoint:'TestEndpoint', server:'ServerStub', path:'str', rest_log_path:'str') -> 'None':
    """ A call with a static bearer token writes no token cache flag.
    """
    cid = _get_cid(path)
    server.add_static_token('test.log.static', 'static.token.1c9e4b7d')

    connection = new_connection(server, endpoint.http_base, path, sec_type=SEC_DEF_TYPE.OAUTH, security_name='test.log.static')
    _ = connection.get(cid)

    request_line, = _get_request_lines(rest_log_path, cid)
    assert request_line.endswith(f'; sec=test.log.static ({SEC_DEF_TYPE.OAUTH}); tok-from-cache=None')

# ################################################################################################################################

def test_lines_with_oauth(endpoint:'TestEndpoint', server:'ServerStub', path:'str', rest_log_path:'str') -> 'None':
    """ Calls with an OAuth bearer token write whether the token was taken from the cache.
    """
    cid = _get_cid(path)

    token_path = path + Token_Path_Suffix
    token_body = dumps({'access_token': 'oauth.token.4b7d1c9e', 'token_type': 'Bearer', 'expires_in': 3600})
    endpoint.set_response(token_path, EndpointResponse(body=token_body, headers=[('Content-Type', 'application/json')]))

    server.add_oauth('test.log.oauth', endpoint.http_base + token_path)

    connection = new_connection(server, endpoint.http_base, path, sec_type=SEC_DEF_TYPE.OAUTH, security_name='test.log.oauth')

    _ = connection.get(cid)
    _ = connection.get(cid)

    first, second = _get_request_lines(rest_log_path, cid)

    assert first.endswith(f'; sec=test.log.oauth ({SEC_DEF_TYPE.OAUTH}); tok-from-cache=False')
    assert second.endswith(f'; sec=test.log.oauth ({SEC_DEF_TYPE.OAUTH}); tok-from-cache=True')

# ################################################################################################################################

def test_lines_with_transport_error(endpoint:'TestEndpoint', server:'ServerStub', path:'str', rest_log_path:'str') -> 'None':
    """ A call that fails before a response arrives writes the request line only.
    """
    cid = _get_cid(path)
    endpoint.set_response(path, EndpointResponse(close_mode=CloseMode.Reset_Before_Response))

    connection = new_connection(server, endpoint.http_base, path)

    with pytest.raises(BackendInvocationError):
        _ = connection.get(cid)

    assert len(_get_request_lines(rest_log_path, cid)) == 1
    assert _get_response_lines(rest_log_path, cid) == []

# ################################################################################################################################

def test_lines_with_retries(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    rest_log_path:'str',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    """ A retried call writes one request line and one response line for each response received.
    """
    monkeypatch.setattr(http_retry, 'sleep', [].append)

    cid = _get_cid(path)
    endpoint.set_responses(path, [EndpointResponse(TOO_MANY_REQUESTS), EndpointResponse(body='After retry')])

    connection = new_connection(server, endpoint.http_base, path, max_retries=1)
    _ = connection.get(cid)

    assert len(_get_request_lines(rest_log_path, cid)) == 1

    first, second = _get_response_lines(rest_log_path, cid)

    _assert_response_line(first, cid, TOO_MANY_REQUESTS, 0)
    _assert_response_line(second, cid, OK, len('After retry'))

# ################################################################################################################################

def test_response_length_is_text_length(endpoint:'TestEndpoint', server:'ServerStub', path:'str', rest_log_path:'str') -> 'None':
    """ The length in a response line is the length of the decoded text of the response.
    """
    cid = _get_cid(path)
    text = 'Łódź, Kraków, Gdańsk'

    endpoint.set_response(path, EndpointResponse(body=text, headers=[('Content-Type', 'text/plain; charset=utf-8')]))

    connection = new_connection(server, endpoint.http_base, path)
    _ = connection.get(cid)

    response_line, = _get_response_lines(rest_log_path, cid)
    _assert_response_line(response_line, cid, OK, len(text))

# ################################################################################################################################
# ################################################################################################################################
