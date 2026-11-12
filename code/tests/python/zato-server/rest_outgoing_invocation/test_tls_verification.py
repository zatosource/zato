# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# TLS verification - the certificate of an endpoint verified against a CA bundle or the default trust store, unless
# the connection or the whole process turns verification off.

# stdlib
from http.client import OK

# pytest
import pytest

# Zato
from zato.common.audit_log.common import TransportStatus
from zato.common.exception import BackendInvocationError
from zato.common.util.tls_verify import Skip_Verify_Env_Key

# Test support
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def test_verified_against_ca_bundle(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A certificate issued by the CA of the bundle is accepted.
    """
    connection = new_connection(server, endpoint.https_base, path, ca_certs_path=endpoint.certificates.ca_path)

    response = connection.get(Test_CID)
    assert response.status_code == OK

    request = endpoint.get_request(path)
    assert request.port == endpoint.https_port

# ################################################################################################################################

def test_verified_by_host_name(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection to a host name is accepted when the certificate is issued for that name.
    """
    connection = new_connection(server, endpoint.https_localhost_base, path, ca_certs_path=endpoint.certificates.ca_path)

    response = connection.get(Test_CID)
    assert response.status_code == OK

    request = endpoint.get_request(path)
    assert request.get_header('Host') == f'localhost:{endpoint.https_port}'

# ################################################################################################################################

def test_verification_off_for_connection(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection that does not validate TLS accepts a certificate of a CA it does not trust.
    """
    connection = new_connection(server, endpoint.https_base, path, validate_tls=False)

    response = connection.get(Test_CID)
    assert response.status_code == OK

# ################################################################################################################################

def test_verification_off_for_process(
    endpoint:'TestEndpoint',
    server:'ServerStub',
    path:'str',
    monkeypatch:'pytest.MonkeyPatch',
    ) -> 'None':
    """ The environment variable that turns verification off for the whole process makes a connection accept
    a certificate of a CA it does not trust.
    """
    monkeypatch.setenv(Skip_Verify_Env_Key, '1')

    connection = new_connection(server, endpoint.https_base, path)

    response = connection.get(Test_CID)
    assert response.status_code == OK

# ################################################################################################################################

def test_untrusted_certificate(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A certificate not issued by the CA of the bundle raises BackendInvocationError with the TLS error transport status.
    """
    connection = new_connection(server, endpoint.https_base, path, ca_certs_path=endpoint.certificates.other_ca_path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.TLS_Error
    assert info.value.args[0].startswith('Connection error: ')
    assert endpoint.get_requests(path) == []

# ################################################################################################################################

def test_default_trust_store(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A connection without a CA bundle verifies against the default trust store, which does not trust the test CA.
    """
    connection = new_connection(server, endpoint.https_base, path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.TLS_Error

# ################################################################################################################################

def test_host_name_mismatch(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A certificate issued for another host name raises BackendInvocationError with the TLS error transport status.
    """
    connection = new_connection(server, endpoint.https_mismatch_base, path, ca_certs_path=endpoint.certificates.ca_path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status == TransportStatus.TLS_Error
    assert endpoint.get_requests(path) == []

# ################################################################################################################################
# ################################################################################################################################
