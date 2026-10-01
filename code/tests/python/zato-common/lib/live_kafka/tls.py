# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The certificates of a Kafka container's TLS listener - the throwaway CA, the listener's own key and certificate
# in the one PEM file Kafka reads them from, and the client's key both as it is and encrypted with a password.

# stdlib
import os
from typing import NamedTuple

# cryptography
from cryptography.hazmat.primitives import serialization

# Zato
from zato.common.crypto.api import CryptoManager

# Test support
from certificates import generate_certificates

# ################################################################################################################################
# ################################################################################################################################

# The files are read by the Kafka process inside the container, which runs under a user of its own
_file_mode = 0o644

# ################################################################################################################################
# ################################################################################################################################

class KafkaTLS(NamedTuple):
    """ The paths a TLS listener and its clients use.
    """
    directory: str
    ca_cert: str
    client_cert: str
    client_key: str
    encrypted_client_key: str
    key_password: str
    broker_pem: str

# ################################################################################################################################
# ################################################################################################################################

def _read_private_key(path:'str') -> 'serialization.PrivateKeyTypes':
    """ One private key, as the certificates helper wrote it.
    """
    with open(path, 'rb') as file_:
        data = file_.read()

    out = serialization.load_pem_private_key(data, password=None)
    return out

# ################################################################################################################################

def _write(path:'str', data:'bytes') -> 'None':
    with open(path, 'wb') as file_:
        _ = file_.write(data)

    os.chmod(path, _file_mode)

# ################################################################################################################################

def _write_broker_pem(path:'str', key_path:'str', cert_path:'str') -> 'None':
    """ The listener's key and certificate in one file - Kafka reads a PEM keystore's key in the PKCS#8 form.
    """
    key = _read_private_key(key_path)

    key_data = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    with open(cert_path, 'rb') as file_:
        cert_data = file_.read()

    _write(path, key_data + cert_data)

# ################################################################################################################################

def _write_encrypted_key(path:'str', key_path:'str', password:'str') -> 'None':
    """ The client's key encrypted with the password.
    """
    key = _read_private_key(key_path)
    encryption = serialization.BestAvailableEncryption(password.encode('utf8'))

    key_data = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        encryption,
    )

    _write(path, key_data)

# ################################################################################################################################

def generate_kafka_tls(directory:'str') -> 'KafkaTLS':
    """ The certificates of one TLS listener, written into the directory.
    """
    paths = generate_certificates(directory)

    key_password = 'key.' + CryptoManager.generate_hex_string()

    out = KafkaTLS(
        directory=directory,
        ca_cert=paths.ca_cert,
        client_cert=paths.client_cert,
        client_key=paths.client_key,
        encrypted_client_key=os.path.join(directory, 'client-encrypted.key'),
        key_password=key_password,
        broker_pem=os.path.join(directory, 'broker.pem'),
    )

    _write_broker_pem(out.broker_pem, paths.server_key, paths.server_cert)
    _write_encrypted_key(out.encrypted_client_key, paths.client_key, key_password)

    return out

# ################################################################################################################################
# ################################################################################################################################
