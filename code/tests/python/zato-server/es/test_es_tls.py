# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Elasticsearch
from elastic_transport import ConnectionError as TransportConnectionError, TlsError
from elasticsearch import AuthenticationException

# Zato
from common import All_Letters, get_client
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from es_server import ESServer
    from certificates import CertificatePaths
    from zato.common.typing_ import stranydict

    CertificatePaths = CertificatePaths
    ESServer = ESServer

# ################################################################################################################################
# ################################################################################################################################

def _get_tls_overrides(certificate_paths:'CertificatePaths') -> 'stranydict':
    """ Returns the configuration overrides that make the client verify the server's certificate
    against the throwaway CA the server's own certificate chains up to.
    """
    out = {
        'tls_ca_certs_file': certificate_paths.ca_cert,
    }

    return out

# ################################################################################################################################

def test_tls_round_trip(es_tls_server:'ESServer', certificate_paths:'CertificatePaths') -> 'None':
    """ A full index-get-update-delete round trip over TLS, with letters from four alphabets
    in the document contents.
    """
    tls_overrides = _get_tls_overrides(certificate_paths)
    client = get_client(es_tls_server, 'test_tls_round_trip', **tls_overrides)

    index_name = 'orders-tls-' + CryptoManager.generate_hex_string().lower()

    # Index a document whose contents use all four alphabets ..
    document = {
        'order_id': 456,
        'customer_name': 'Test customer ' + All_Letters,
        'status': 'ready',
    }
    index_response = client.index(index=index_name, id='order-456', document=document)
    assert index_response['result'] == 'created'

    # .. read it back and confirm the Unicode round trip was exact ..
    found = client.get(index=index_name, id='order-456')
    assert found['_source']['customer_name'] == 'Test customer ' + All_Letters

    # .. update it ..
    _ = client.update(index=index_name, id='order-456', doc={'status': 'shipped ' + All_Letters})

    found = client.get(index=index_name, id='order-456')
    assert found['_source']['status'] == 'shipped ' + All_Letters

    # .. delete it ..
    delete_response = client.delete(index=index_name, id='order-456')
    assert delete_response['result'] == 'deleted'

    # .. and confirm it is gone.
    assert not client.exists(index=index_name, id='order-456')

    # Clean up the index itself
    _ = client.indices.delete(index=index_name)

# ################################################################################################################################

def test_mutual_tls(es_tls_server:'ESServer', certificate_paths:'CertificatePaths') -> 'None':
    """ A client that presents its own certificate - the combined pem under tls_cert_key_file -
    can talk to the server too, because the server accepts optional client certificates.
    """
    client_pem = os.path.join(certificate_paths.directory, 'client.pem')

    client = get_client(
        es_tls_server,
        'test_mutual_tls',
        tls_ca_certs_file=certificate_paths.ca_cert,
        tls_cert_key_file=client_pem,
    )

    _ = client.info()

# ################################################################################################################################

def test_tls_validation_disabled(es_tls_server:'ESServer') -> 'None':
    """ With certificate validation off, no CA file is needed to talk to the server.
    """
    client = get_client(es_tls_server, 'test_tls_validation_disabled', is_tls_validation_enabled=False)
    _ = client.info()

# ################################################################################################################################

def test_non_tls_client_fails_against_tls_server(es_tls_server:'ESServer') -> 'None':
    """ A client speaking plain http must not be able to talk to a server that requires TLS.
    """
    one_address = f'http://{es_tls_server.host}:{es_tls_server.port}'
    client = get_client(es_tls_server, 'test_non_tls_client_fails_against_tls_server', address_list=one_address)

    with pytest.raises((TransportConnectionError, TlsError)):
        _ = client.info()

# ################################################################################################################################

def test_wrong_password(es_tls_server:'ESServer', certificate_paths:'CertificatePaths') -> 'None':
    """ A connection with a wrong password must fail to authenticate.
    """
    client = get_client(
        es_tls_server,
        'test_wrong_password',
        tls_ca_certs_file=certificate_paths.ca_cert,
        secret='wrong-password-on-purpose',
    )

    with pytest.raises(AuthenticationException):
        _ = client.info()

# ################################################################################################################################
# ################################################################################################################################
