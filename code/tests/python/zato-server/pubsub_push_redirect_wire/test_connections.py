# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The connections of redirected pushes - the forms of the body of a redirect, the reuse of the connection
# after a redirect, targets that cannot be reached, and attempts that start at the configured address.

# stdlib
from http.client import PERMANENT_REDIRECT, SERVICE_UNAVAILABLE

# pytest
import pytest

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError, HTTPError

# Zato
from zato.common.test.reservation import reserve_port

# Test support
from http_endpoint.endpoint import EndpointResponse, Host, UnresponsiveListener
from redirect_wire_support import Delivery, new_message, new_payload, redirect_to

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from rest_outgoing_stub.connection import ServerStub
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The size of the payload of each push
_payload_size = 256

# The body of the redirects that have one
_redirect_body = 'The endpoint of the orders moved to the archive.'

# The timeout of the connection whose redirect leads to a listener that never accepts, in seconds
_short_timeout = 1

# The purpose under which the port without a listener is reserved
_port_purpose = 'pubsub-push-redirect-no-listener'

# The forms of the response of a redirect
_redirect_forms:'dict[str, anydict]' = {
    'body': {'body': _redirect_body},
    'chunked': {'body': _redirect_body, 'is_chunked': True},
    'no-length': {'body': _redirect_body, 'has_no_length': True},
    'connection-close': {'body': _redirect_body, 'needs_close': True},
}

_redirect_form_names = list(_redirect_forms)

# ################################################################################################################################
# ################################################################################################################################

def _new_message() -> 'anydict':
    payload = new_payload(_payload_size)

    out = new_message(payload)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('form', _redirect_form_names)
def test_redirect_with_each_form_of_body_is_followed(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    loopback_second:'TestEndpoint',
    path:'str',
    form:'str',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_second.http_base + target_path

    kwargs = _redirect_forms[form]
    response = redirect_to(target, **kwargs)
    loopback_first.set_responses(source_path, [response])

    message = _new_message()

    delivery = Delivery(server, loopback_first.http_base, source_path)
    delivery.push(message)

    target_request = loopback_second.get_request(target_path)
    assert target_request.method == 'POST'

# ################################################################################################################################

def test_connection_is_reused_after_a_redirect_with_a_body(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    loopback_second:'TestEndpoint',
    path:'str',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_second.http_base + target_path

    response = redirect_to(target, body=_redirect_body)
    loopback_first.set_responses(source_path, [response])

    delivery = Delivery(server, loopback_first.http_base, source_path)

    first_message = _new_message()
    second_message = _new_message()

    delivery.push(first_message)
    delivery.push(second_message)

    # The body of the first redirect was read in full, so the second push went out on the same connection
    first_request, second_request = loopback_first.get_requests(source_path)
    assert second_request.connection_id == first_request.connection_id

    target_requests = loopback_second.get_requests(target_path)
    target_count = len(target_requests)

    assert target_count == 2

# ################################################################################################################################

def test_redirect_to_port_without_listener_fails(server:'ServerStub', loopback_first:'TestEndpoint', path:'str') -> 'None':

    reservation = reserve_port(_port_purpose)

    try:
        target = f'http://{Host}:{reservation.port}{path}/target'

        response = redirect_to(target)
        loopback_first.set_responses(path, [response])

        message = _new_message()
        delivery = Delivery(server, loopback_first.http_base, path)

        with pytest.raises(RequestsConnectionError):
            delivery.push(message)

    finally:
        reservation.release()

# ################################################################################################################################

def test_redirect_to_listener_that_never_accepts_fails(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    ) -> 'None':

    listener = UnresponsiveListener()
    listener.start()

    try:
        target = listener.base + path + '/target'

        response = redirect_to(target)
        loopback_first.set_responses(path, [response])

        message = _new_message()
        delivery = Delivery(server, loopback_first.http_base, path, timeout=_short_timeout)

        with pytest.raises(RequestsConnectionError):
            delivery.push(message)

    finally:
        listener.stop()

# ################################################################################################################################

def test_next_attempt_starts_at_the_configured_address(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    loopback_second:'TestEndpoint',
    path:'str',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_second.http_base + target_path

    # The source moved permanently, and the target fails the first push and accepts the next one
    source_response = redirect_to(target, PERMANENT_REDIRECT)
    loopback_first.set_responses(source_path, [source_response])

    unavailable = EndpointResponse(SERVICE_UNAVAILABLE)
    accepted = EndpointResponse()

    loopback_second.set_responses(target_path, [unavailable, accepted])

    message = _new_message()
    delivery = Delivery(server, loopback_first.http_base, source_path)

    with pytest.raises(HTTPError):
        delivery.push(message)

    # The next attempt goes to the configured address first, not to the target it was redirected to before
    message['delivery_attempt'] = 2
    delivery.push(message)

    source_requests = loopback_first.get_requests(source_path)
    target_requests = loopback_second.get_requests(target_path)

    source_count = len(source_requests)
    target_count = len(target_requests)

    assert source_count == 2
    assert target_count == 2

# ################################################################################################################################
# ################################################################################################################################
