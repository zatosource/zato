# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# PyMongo
from pymongo.errors import ServerSelectionTimeoutError

# Zato
from common import All_Letters, get_client
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from containers import MongoDBServer
    from certificates import CertificatePaths
    from zato.common.typing_ import stranydict

    CertificatePaths = CertificatePaths
    MongoDBServer = MongoDBServer

# ################################################################################################################################
# ################################################################################################################################

# The database all the tests below use
_test_db_name = 'zato_test_mongodb_tls'

# ################################################################################################################################
# ################################################################################################################################

def _get_tls_overrides(certificate_paths:'CertificatePaths') -> 'stranydict':
    """ Returns the configuration overrides that turn TLS on, with the combined client pem
    that pymongo 4 expects under its tlsCertificateKeyFile option.
    """
    client_pem = os.path.join(certificate_paths.directory, 'client.pem')

    out = {
        'is_tls_enabled': True,
        'tls_ca_certs_file': certificate_paths.ca_cert,
        'tls_cert_key_file': client_pem,
    }

    return out

# ################################################################################################################################

def test_tls_round_trip(mongodb_tls_server:'MongoDBServer', certificate_paths:'CertificatePaths') -> 'None':
    """ A full insert-find-update-delete round trip over TLS, with letters from four alphabets
    in the collection name and in the document contents.
    """
    tls_overrides = _get_tls_overrides(certificate_paths)
    client = get_client(mongodb_tls_server, 'test_tls_round_trip', **tls_overrides)

    db = client[_test_db_name]

    collection_name = 'orders_' + All_Letters + '_' + CryptoManager.generate_hex_string()
    collection = db[collection_name]

    # Insert a document whose contents use all four alphabets ..
    document = {
        'order_id': 456,
        'customer_name': 'Test customer ' + All_Letters,
        'status': 'ready',
    }
    insert_result = collection.insert_one(document)

    # .. find it back and confirm the Unicode round trip was exact ..
    found = collection.find_one({'order_id': 456})
    assert found is not None
    assert found['_id'] == insert_result.inserted_id
    assert found['customer_name'] == 'Test customer ' + All_Letters

    # .. update it ..
    update_result = collection.update_one({'order_id': 456}, {'$set': {'status': 'shipped ' + All_Letters}})
    assert update_result.modified_count == 1

    found = collection.find_one({'order_id': 456})
    assert found is not None
    assert found['status'] == 'shipped ' + All_Letters

    # .. delete it ..
    delete_result = collection.delete_one({'order_id': 456})
    assert delete_result.deleted_count == 1

    # .. and confirm it is gone.
    found = collection.find_one({'order_id': 456})
    assert found is None

# ################################################################################################################################

def test_non_tls_client_fails_against_tls_server(mongodb_tls_server:'MongoDBServer') -> 'None':
    """ A client without TLS enabled must not be able to talk to a server that requires TLS.
    """
    client = get_client(mongodb_tls_server, 'test_non_tls_client_fails_against_tls_server')

    with pytest.raises(ServerSelectionTimeoutError):
        _ = client.admin.command('ping')

# ################################################################################################################################
# ################################################################################################################################
