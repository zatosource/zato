# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Client certificates - the certificate a connection presents to an endpoint that requires one, from a single PEM file
# or from a separate certificate and key, from the connection itself or from an mTLS definition, and read anew
# from its files once the TLS material is reloaded.

# stdlib
import os
import shutil

# pytest
import pytest

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.audit_log.common import TransportStatus
from zato.common.exception import BackendInvocationError

# Test support
from endpoint_certificates import Client_First_Common_Name, Client_Second_Common_Name
from support import new_connection, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from endpoint import TestEndpoint
    from support import ServerStub

# ################################################################################################################################
# ################################################################################################################################

def test_single_pem_file(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A single PEM file with the certificate and its key is presented to the endpoint.
    """
    certificates = endpoint.certificates

    connection = new_connection(
        server,
        endpoint.https_mtls_base,
        path,
        ca_certs_path=certificates.ca_path,
        tls_client_cert=certificates.client_first_path,
    )

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)
    assert request.client_common_name == Client_First_Common_Name

# ################################################################################################################################

def test_separate_certificate_and_key(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ A certificate and a key in separate files are presented to the endpoint.
    """
    certificates = endpoint.certificates

    connection = new_connection(
        server,
        endpoint.https_mtls_base,
        path,
        ca_certs_path=certificates.ca_path,
        tls_client_cert=certificates.client_second_cert_path,
        tls_client_key=certificates.client_second_key_path,
    )

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)
    assert request.client_common_name == Client_Second_Common_Name

# ################################################################################################################################

def test_mtls_definition_replaces_connection_material(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ The certificate of an mTLS definition is presented instead of the one the connection itself is configured with.
    """
    certificates = endpoint.certificates

    connection = new_connection(
        server,
        endpoint.https_mtls_base,
        path,
        sec_type=SEC_DEF_TYPE.MTLS,
        ca_certs_path=certificates.ca_path,
        tls_client_cert=certificates.client_first_path,
        cert_path=certificates.client_second_cert_path,
        key_path=certificates.client_second_key_path,
    )

    _ = connection.get(Test_CID)

    request = endpoint.get_request(path)
    assert request.client_common_name == Client_Second_Common_Name

# ################################################################################################################################

def test_reload_tls_material(endpoint:'TestEndpoint', server:'ServerStub', path:'str', tmp_path:'os.PathLike') -> 'None':
    """ A certificate file replaced on disk is presented once the TLS material is reloaded, and not before.
    """
    certificates = endpoint.certificates

    client_path = os.path.join(str(tmp_path), 'client.pem')
    _ = shutil.copyfile(certificates.client_first_path, client_path)

    connection = new_connection(
        server,
        endpoint.https_mtls_base,
        path,
        ca_certs_path=certificates.ca_path,
        tls_client_cert=client_path,
    )

    # The first certificate is presented ..
    _ = connection.get(Test_CID)

    # .. the file is replaced with the second certificate and its key ..
    with open(certificates.client_second_cert_path, 'rb') as file:
        second_cert = file.read()

    with open(certificates.client_second_key_path, 'rb') as file:
        second_key = file.read()

    with open(client_path, 'wb') as file:
        _ = file.write(second_cert + second_key)

    # .. the pooled connection keeps presenting the first one ..
    _ = connection.get(Test_CID)

    # .. until the material is reloaded.
    connection.reload_tls_material()
    _ = connection.get(Test_CID)

    first, second, third = endpoint.get_requests(path)

    assert first.client_common_name == Client_First_Common_Name
    assert second.client_common_name == Client_First_Common_Name
    assert third.client_common_name == Client_Second_Common_Name

# ################################################################################################################################

def test_no_client_certificate(endpoint:'TestEndpoint', server:'ServerStub', path:'str') -> 'None':
    """ An endpoint that requires a client certificate rejects a connection that presents none,
    which raises BackendInvocationError with a connection-level transport status.
    """
    certificates = endpoint.certificates

    connection = new_connection(server, endpoint.https_mtls_base, path, ca_certs_path=certificates.ca_path)

    with pytest.raises(BackendInvocationError) as info:
        _ = connection.get(Test_CID)

    assert info.value.transport_status in (TransportStatus.TLS_Error, TransportStatus.Connection_Error)
    assert endpoint.get_requests(path) == []

# ################################################################################################################################
# ################################################################################################################################
