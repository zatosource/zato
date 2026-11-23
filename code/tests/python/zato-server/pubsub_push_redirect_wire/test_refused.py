# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Redirects of a push that are not followed - each of them fails the attempt and the target receives nothing.

# stdlib
from http.client import FOUND, MOVED_PERMANENTLY, MULTIPLE_CHOICES, NOT_MODIFIED, SEE_OTHER, TEMPORARY_REDIRECT, USE_PROXY

# pytest
import pytest

# requests
from requests.exceptions import HTTPError

# Zato
from zato.server.base.parallel.delivery_rest import PushRedirectError

# Test support
from http_endpoint.endpoint import EndpointResponse
from redirect_wire_support import Delivery, new_message, new_payload, redirect_to

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from rest_outgoing_stub.connection import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The status that the endpoint sends for 306, which http.client does not name
_switch_proxy = 306

# The size of the payload of each push
_payload_size = 256

# ################################################################################################################################
# ################################################################################################################################

def _push_and_fail(
    server:'ServerStub',
    endpoint:'TestEndpoint',
    source_path:'str',
    error_class:'type[Exception]',
    ) -> 'None':
    """ Delivers a message to the source on the plain HTTP listener and expects the attempt to fail with the error class.
    """
    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery = Delivery(server, endpoint.http_base, source_path)

    with pytest.raises(error_class):
        delivery.push(message)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('status', [
    MULTIPLE_CHOICES, MOVED_PERMANENTLY, FOUND, SEE_OTHER, NOT_MODIFIED, USE_PROXY, _switch_proxy,
])
def test_status_other_than_307_and_308_fails(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    status:'int',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_first.http_base + target_path

    response = redirect_to(target, status)
    loopback_first.set_responses(source_path, [response])

    _push_and_fail(server, loopback_first, source_path, HTTPError)

    target_requests = loopback_first.get_requests(target_path)
    assert target_requests == []

# ################################################################################################################################

def test_redirect_without_location_fails(server:'ServerStub', loopback_first:'TestEndpoint', path:'str') -> 'None':

    response = EndpointResponse(TEMPORARY_REDIRECT)
    loopback_first.set_responses(path, [response])

    _push_and_fail(server, loopback_first, path, PushRedirectError)

    requests = loopback_first.get_requests(path)
    request_count = len(requests)

    assert request_count == 1

# ################################################################################################################################

@pytest.mark.parametrize('location', [
    'ftp://files.example.com/orders',
    'file:///etc/hosts',
    'javascript:alert(1)',
    'market://details?id=42',
])
def test_redirect_with_another_scheme_fails(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    location:'str',
    ) -> 'None':

    response = redirect_to(location)
    loopback_first.set_responses(path, [response])

    _push_and_fail(server, loopback_first, path, PushRedirectError)

# ################################################################################################################################

@pytest.mark.parametrize('kind', ['user', 'user-password', 'no-host', 'no-host-port', 'port-zero', 'port-too-high'])
def test_redirect_with_invalid_authority_fails(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    kind:'str',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    port = loopback_first.http_port

    locations = {
        'user': f'http://john.smith@127.0.0.1:{port}{target_path}',
        'user-password': f'http://john.smith:Test.2026@127.0.0.1:{port}{target_path}',
        'no-host': f'http://:{port}{target_path}',
        'no-host-port': 'https://:443/',
        'port-zero': f'http://127.0.0.1:0{target_path}',
        'port-too-high': f'http://127.0.0.1:70000{target_path}',
    }

    location = locations[kind]

    response = redirect_to(location)
    loopback_first.set_responses(source_path, [response])

    _push_and_fail(server, loopback_first, source_path, PushRedirectError)

    target_requests = loopback_first.get_requests(target_path)
    assert target_requests == []

# ################################################################################################################################

def test_redirect_from_https_to_http_fails(server:'ServerStub', loopback_first:'TestEndpoint', path:'str') -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_first.http_base + target_path

    response = redirect_to(target)
    loopback_first.set_responses(source_path, [response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    ca_path = loopback_first.certificates.ca_path
    delivery = Delivery(server, loopback_first.https_base, source_path, ca_certs_path=ca_path)

    with pytest.raises(PushRedirectError):
        delivery.push(message)

    # The source received the push over TLS and the target received nothing
    source_requests = loopback_first.get_requests(source_path)
    target_requests = loopback_first.get_requests(target_path)

    source_count = len(source_requests)

    assert source_count == 1
    assert target_requests == []

# ################################################################################################################################
# ################################################################################################################################
