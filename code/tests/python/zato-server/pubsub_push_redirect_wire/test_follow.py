# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Redirects of a push that are followed - the address each hop reaches, the body and the headers
# that each hop receives, and the limit of the number of redirects.

# stdlib
from http.client import PERMANENT_REDIRECT, TEMPORARY_REDIRECT

# pytest
import pytest

# Zato
from zato.server.base.parallel.delivery_rest import Max_Push_Redirects, PushRedirectError

# Test support
from redirect_wire_support import Absent_Headers, Delivery, new_message, new_payload, Push_Headers, redirect_to

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from rest_outgoing_stub.connection import ServerStub
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The statuses of the redirects that are followed
_statuses = [TEMPORARY_REDIRECT, PERMANENT_REDIRECT]

# The sizes of the payloads whose bodies are compared
_payload_sizes = [0, 1, 64 * 1024, 16 * 1024 * 1024]

# The payload of the tests that do not compare sizes
_payload_size = 256

# ################################################################################################################################
# ################################################################################################################################

def _get_target(kind:'str', first:'TestEndpoint', second:'TestEndpoint', target_path:'str') -> 'str':
    """ Returns the address of the target of a redirect - on the same listener, on another port, or under the localhost alias.
    """
    if kind == 'path':
        out = first.http_base + target_path

    elif kind == 'port':
        out = second.http_base + target_path

    # .. anything else is the localhost alias of the same listener.
    else:
        out = f'http://localhost:{first.http_port}{target_path}'

    return out

# ################################################################################################################################

def _get_chain_paths(path:'str', hop_count:'int') -> 'strlist':
    """ Returns the paths of a chain of redirects, the source first and the final target last.
    """
    out:'strlist' = []

    for index in range(hop_count + 1):
        hop_path = f'{path}/hop-{index}'
        out.append(hop_path)

    return out

# ################################################################################################################################

def _set_chain(endpoint:'TestEndpoint', paths:'strlist') -> 'None':
    """ Makes each path of the chain redirect to the next one, with the last one accepting the push.
    """
    redirect_count = len(paths) - 1

    for index in range(redirect_count):
        current = paths[index]
        next_path = paths[index + 1]
        location = endpoint.http_base + next_path

        response = redirect_to(location)
        endpoint.set_responses(current, [response])

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('status', _statuses)
@pytest.mark.parametrize('kind', ['path', 'port', 'localhost'])
def test_redirect_is_delivered(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    loopback_second:'TestEndpoint',
    path:'str',
    status:'int',
    kind:'str',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = _get_target(kind, loopback_first, loopback_second, target_path)

    response = redirect_to(target, status)
    loopback_first.set_responses(source_path, [response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery = Delivery(server, loopback_first.http_base, source_path)
    delivery.push(message)

    # The source received the push once and the target received it once
    source_requests = loopback_first.get_requests(source_path)
    target_requests = loopback_first.get_requests(target_path) + loopback_second.get_requests(target_path)

    source_count = len(source_requests)
    target_count = len(target_requests)

    assert source_count == 1
    assert target_count == 1

# ################################################################################################################################

@pytest.mark.parametrize('status', _statuses)
@pytest.mark.parametrize('payload_size', _payload_sizes)
def test_body_is_the_body_of_a_direct_push(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    status:'int',
    payload_size:'int',
    ) -> 'None':

    direct_path = path + '/direct'
    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_first.http_base + target_path

    response = redirect_to(target, status)
    loopback_first.set_responses(source_path, [response])

    payload = new_payload(payload_size)
    message = new_message(payload)

    # The same message is pushed once directly and once through the redirect ..
    direct = Delivery(server, loopback_first.http_base, direct_path)
    direct.push(message)

    redirected = Delivery(server, loopback_first.http_base, source_path)
    redirected.push(message)

    direct_request = loopback_first.get_request(direct_path)
    source_request = loopback_first.get_request(source_path)
    target_request = loopback_first.get_request(target_path)

    # .. and each hop received the same bytes with the same length.
    direct_length = direct_request.get_header('Content-Length')
    source_length = source_request.get_header('Content-Length')
    target_length = target_request.get_header('Content-Length')

    assert source_request.body == direct_request.body
    assert target_request.body == direct_request.body

    assert source_length == direct_length
    assert target_length == direct_length

# ################################################################################################################################

@pytest.mark.parametrize('status', _statuses)
def test_method_and_headers_are_kept(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    loopback_second:'TestEndpoint',
    path:'str',
    status:'int',
    ) -> 'None':

    source_path = path + '/source'
    middle_path = path + '/middle'
    target_path = path + '/target'

    middle = loopback_second.http_base + middle_path
    target = loopback_first.http_base + target_path

    # The source sets a cookie, which is not sent to any later hop
    cookie_header = [('Set-Cookie', 'session=4f2a9c1e; Path=/')]

    source_response = redirect_to(middle, status)
    source_response.headers.extend(cookie_header)

    middle_response = redirect_to(target, status)

    loopback_first.set_responses(source_path, [source_response])
    loopback_second.set_responses(middle_path, [middle_response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery = Delivery(server, loopback_first.http_base, source_path)
    delivery.push(message)

    source_request = loopback_first.get_request(source_path)
    middle_request = loopback_second.get_request(middle_path)
    target_request = loopback_first.get_request(target_path)

    for request in (source_request, middle_request, target_request):

        assert request.method == 'POST'

        for name in Push_Headers:
            value = request.get_header(name)
            expected = source_request.get_header(name)

            assert value is not None
            assert value == expected

        for name in Absent_Headers:
            value = request.get_header(name)
            assert value is None

# ################################################################################################################################

def test_chain_at_the_limit_is_delivered(server:'ServerStub', loopback_first:'TestEndpoint', path:'str') -> 'None':

    paths = _get_chain_paths(path, Max_Push_Redirects)
    _set_chain(loopback_first, paths)

    payload = new_payload(_payload_size)
    message = new_message(payload)

    source_path = paths[0]
    target_path = paths[-1]

    delivery = Delivery(server, loopback_first.http_base, source_path)
    delivery.push(message)

    # Each hop of the chain received the push once, the final target included
    for hop_path in paths:
        requests = loopback_first.get_requests(hop_path)
        request_count = len(requests)

        assert request_count == 1, hop_path

    target_request = loopback_first.get_request(target_path)
    assert target_request.method == 'POST'

# ################################################################################################################################

def test_chain_beyond_the_limit_fails(server:'ServerStub', loopback_first:'TestEndpoint', path:'str') -> 'None':

    hop_count = Max_Push_Redirects + 1

    paths = _get_chain_paths(path, hop_count)
    _set_chain(loopback_first, paths)

    payload = new_payload(_payload_size)
    message = new_message(payload)

    source_path = paths[0]
    target_path = paths[-1]

    delivery = Delivery(server, loopback_first.http_base, source_path)

    with pytest.raises(PushRedirectError):
        delivery.push(message)

    # The final target received nothing
    target_requests = loopback_first.get_requests(target_path)
    assert target_requests == []

# ################################################################################################################################

@pytest.mark.parametrize('status', _statuses)
def test_redirect_to_itself_fails(server:'ServerStub', loopback_first:'TestEndpoint', path:'str', status:'int') -> 'None':

    source = loopback_first.http_base + path

    response = redirect_to(source, status)
    loopback_first.set_responses(path, [response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery = Delivery(server, loopback_first.http_base, path)

    with pytest.raises(PushRedirectError):
        delivery.push(message)

    # The first push and each redirect followed reached the same address
    requests = loopback_first.get_requests(path)

    request_count = len(requests)
    expected_count = Max_Push_Redirects + 1

    assert request_count == expected_count

# ################################################################################################################################
# ################################################################################################################################
