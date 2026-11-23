# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Redirects of a push from plain HTTP to TLS - with the certificate of the endpoint verified against its CA,
# with a certificate that names another host, and with a client certificate.

# pytest
import pytest

# requests
from requests.exceptions import SSLError

# Test support
from http_endpoint.endpoint_certificates import Client_First_Common_Name
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

# ################################################################################################################################
# ################################################################################################################################

def test_redirect_to_https_is_delivered(server:'ServerStub', loopback_first:'TestEndpoint', path:'str') -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_first.https_base + target_path

    response = redirect_to(target)
    loopback_first.set_responses(source_path, [response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    ca_path = loopback_first.certificates.ca_path
    delivery = Delivery(server, loopback_first.http_base, source_path, ca_certs_path=ca_path)
    delivery.push(message)

    # The target received the push on the TLS listener
    source_request = loopback_first.get_request(source_path)
    target_request = loopback_first.get_request(target_path)

    assert target_request.port == loopback_first.https_port
    assert target_request.body == source_request.body

# ################################################################################################################################

def test_redirect_to_certificate_of_another_host_fails(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_first.https_mismatch_base + target_path

    response = redirect_to(target)
    loopback_first.set_responses(source_path, [response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    ca_path = loopback_first.certificates.ca_path
    delivery = Delivery(server, loopback_first.http_base, source_path, ca_certs_path=ca_path)

    with pytest.raises(SSLError):
        delivery.push(message)

    target_requests = loopback_first.get_requests(target_path)
    assert target_requests == []

# ################################################################################################################################

def test_redirect_to_listener_with_client_certificates(
    server:'ServerStub',
    loopback_first:'TestEndpoint',
    path:'str',
    ) -> 'None':

    source_path = path + '/source'
    target_path = path + '/target'
    target = loopback_first.https_mtls_base + target_path

    response = redirect_to(target)
    loopback_first.set_responses(source_path, [response])

    payload = new_payload(_payload_size)
    message = new_message(payload)

    certificates = loopback_first.certificates

    delivery = Delivery(
        server,
        loopback_first.http_base,
        source_path,
        ca_certs_path=certificates.ca_path,
        tls_client_cert=certificates.client_first_path,
    )
    delivery.push(message)

    # The target received the push with the client certificate of the connection
    target_request = loopback_first.get_request(target_path)

    assert target_request.port == loopback_first.https_mtls_port
    assert target_request.client_common_name == Client_First_Common_Name

# ################################################################################################################################
# ################################################################################################################################
