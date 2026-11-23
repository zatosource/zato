# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The network scope of redirects - a redirect is followed within the scope of the address of the first push
# and fails, with nothing sent, to an address of another scope.

# pytest
import pytest

# requests
from requests.exceptions import ConnectionError as RequestsConnectionError

# Test support
from redirect_wire_support import Delivery, new_message, new_payload, redirect_to

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from http_endpoint.endpoint import TestEndpoint
    from rest_outgoing_stub.connection import ServerStub

# ################################################################################################################################
# ################################################################################################################################

# The size of the payload of each push
_payload_size = 256

# What the error of a hop names when its address is outside the scope of the first push
_scope_refused_text = 'required network scope'

# ################################################################################################################################
# ################################################################################################################################

def _redirect(
    server:'ServerStub',
    source:'TestEndpoint',
    target:'TestEndpoint',
    path:'str',
    ) -> 'Delivery':
    """ Makes the source redirect to the target and returns the delivery of a subscription whose endpoint is the source.
    """
    source_path = path + '/source'
    target_path = path + '/target'
    location = target.http_base + target_path

    response = redirect_to(location)
    source.set_responses(source_path, [response])

    out = Delivery(server, source.http_base, source_path)
    return out

# ################################################################################################################################

def _push(delivery:'Delivery') -> 'None':
    """ Delivers one message.
    """
    payload = new_payload(_payload_size)
    message = new_message(payload)

    delivery.push(message)

# ################################################################################################################################
# ################################################################################################################################

def test_redirect_within_the_non_loopback_address_is_delivered(
    server:'ServerStub',
    remote_first:'TestEndpoint',
    remote_second:'TestEndpoint',
    path:'str',
    ) -> 'None':

    delivery = _redirect(server, remote_first, remote_second, path)
    _push(delivery)

    target_path = path + '/target'
    target_request = remote_second.get_request(target_path)

    assert target_request.method == 'POST'

# ################################################################################################################################

def test_redirect_within_the_loopback_address_is_delivered(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    loopback_second:'TestEndpoint',
    path:'str',
    ) -> 'None':

    delivery = _redirect(server, loopback_first, loopback_second, path)
    _push(delivery)

    target_path = path + '/target'
    target_request = loopback_second.get_request(target_path)

    assert target_request.method == 'POST'

# ################################################################################################################################

@pytest.mark.parametrize('direction', ['to-loopback', 'from-loopback'])
def test_redirect_to_another_scope_fails(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    remote_first:'TestEndpoint',
    path:'str',
    direction:'str',
    ) -> 'None':

    if direction == 'to-loopback':
        source = remote_first
        target = loopback_first
    else:
        source = loopback_first
        target = remote_first

    delivery = _redirect(server, source, target, path)

    with pytest.raises(RequestsConnectionError, match=_scope_refused_text):
        _push(delivery)

    # The source received the push and the target received nothing
    source_path = path + '/source'
    target_path = path + '/target'

    source_requests = source.get_requests(source_path)
    target_requests = target.get_requests(target_path)

    source_count = len(source_requests)

    assert source_count == 1
    assert target_requests == []

# ################################################################################################################################

def test_chain_that_leaves_the_scope_fails_at_that_hop(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    loopback_second:'TestEndpoint',
    remote_first:'TestEndpoint',
    path:'str',
    ) -> 'None':

    source_path = path + '/source'
    middle_path = path + '/middle'
    target_path = path + '/target'

    middle = loopback_second.http_base + middle_path
    target = remote_first.http_base + target_path

    # The first hop stays on the loopback address and the second one leaves it
    source_response = redirect_to(middle)
    middle_response = redirect_to(target)

    loopback_first.set_responses(source_path, [source_response])
    loopback_second.set_responses(middle_path, [middle_response])

    delivery = Delivery(server, loopback_first.http_base, source_path)

    with pytest.raises(RequestsConnectionError, match=_scope_refused_text):
        _push(delivery)

    middle_requests = loopback_second.get_requests(middle_path)
    target_requests = remote_first.get_requests(target_path)

    middle_count = len(middle_requests)

    assert middle_count == 1
    assert target_requests == []

# ################################################################################################################################
# ################################################################################################################################
