# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The certificates the test endpoint and the outgoing connections use, generated once per run - a CA with
# the server certificates it issued, an unrelated CA, and a client CA with two client certificates.

# stdlib
import os
from datetime import datetime, timedelta, timezone
from ipaddress import IPv4Address

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

# ################################################################################################################################
# ################################################################################################################################

# How long every generated certificate is valid for
_validity = timedelta(days=2)

# The host names and addresses the certificates are issued for
_loopback_address = IPv4Address('127.0.0.1')
_localhost_name = 'localhost'
_mismatch_name = 'other.example'

# The common names of the two client certificates
Client_First_Common_Name  = 'client.first'
Client_Second_Common_Name = 'client.second'

# ################################################################################################################################
# ################################################################################################################################

class _Issued:
    """ One generated certificate with its private key.
    """

    def __init__(self, cert:'x509.Certificate', key:'EllipticCurvePrivateKey') -> 'None':
        self.cert = cert
        self.key = key

# ################################################################################################################################

    @property
    def cert_pem(self) -> 'bytes':
        out = self.cert.public_bytes(serialization.Encoding.PEM)
        return out

    @property
    def key_pem(self) -> 'bytes':
        out = self.key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_name(common_name:'str') -> 'x509.Name':
    attribute = x509.NameAttribute(NameOID.COMMON_NAME, common_name)
    out = x509.Name([attribute])
    return out

# ################################################################################################################################

def _new_ca(common_name:'str') -> '_Issued':
    """ Generates a self-signed CA certificate.
    """
    key = ec.generate_private_key(ec.SECP256R1())
    name = _new_name(common_name)
    now = datetime.now(timezone.utc)
    serial_number = x509.random_serial_number()
    public_key = key.public_key()
    constraints = x509.BasicConstraints(ca=True, path_length=None)

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(serial_number)
    builder = builder.not_valid_before(now - timedelta(minutes=5))
    builder = builder.not_valid_after(now + _validity)
    builder = builder.add_extension(constraints, critical=True)

    cert = builder.sign(key, hashes.SHA256())

    out = _Issued(cert, key)
    return out

# ################################################################################################################################

def _issue(ca:'_Issued', common_name:'str', alternative_names:'list[x509.GeneralName]', is_client:'bool') -> '_Issued':
    """ Generates a certificate issued by the CA.
    """
    key = ec.generate_private_key(ec.SECP256R1())
    name = _new_name(common_name)
    now = datetime.now(timezone.utc)
    serial_number = x509.random_serial_number()
    public_key = key.public_key()
    constraints = x509.BasicConstraints(ca=False, path_length=None)

    if is_client:
        usage = x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH])
    else:
        usage = x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH])

    builder = x509.CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(ca.cert.subject)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(serial_number)
    builder = builder.not_valid_before(now - timedelta(minutes=5))
    builder = builder.not_valid_after(now + _validity)
    builder = builder.add_extension(constraints, critical=True)
    builder = builder.add_extension(usage, critical=False)

    if alternative_names:
        subject_alternative_name = x509.SubjectAlternativeName(alternative_names)
        builder = builder.add_extension(subject_alternative_name, critical=False)

    cert = builder.sign(ca.key, hashes.SHA256())

    out = _Issued(cert, key)
    return out

# ################################################################################################################################
# ################################################################################################################################

class CertificateSet:
    """ The certificate files of one run, all of them in one directory.
    """

    def __init__(self, directory:'str') -> 'None':
        self.directory = directory

        # The CA the endpoint's server certificates are issued by and an unrelated one
        self.ca_path = os.path.join(directory, 'ca.pem')
        self.other_ca_path = os.path.join(directory, 'other-ca.pem')

        # The certificate for the loopback address and localhost, and the one for another host name
        self.server_cert_path = os.path.join(directory, 'server-cert.pem')
        self.server_key_path = os.path.join(directory, 'server-key.pem')
        self.mismatch_cert_path = os.path.join(directory, 'mismatch-cert.pem')
        self.mismatch_key_path = os.path.join(directory, 'mismatch-key.pem')

        # The CA the client certificates are issued by, the first client certificate in a single file with its key,
        # and the second one with its key in a separate file
        self.client_ca_path = os.path.join(directory, 'client-ca.pem')
        self.client_first_path = os.path.join(directory, 'client-first.pem')
        self.client_second_cert_path = os.path.join(directory, 'client-second-cert.pem')
        self.client_second_key_path = os.path.join(directory, 'client-second-key.pem')

# ################################################################################################################################

    def _write(self, path:'str', data:'bytes') -> 'None':
        with open(path, 'wb') as file:
            _ = file.write(data)

# ################################################################################################################################

    def generate(self) -> 'None':
        """ Generates all the certificates and writes them to their files.
        """
        os.makedirs(self.directory, exist_ok=True)

        # The server side ..
        ca = _new_ca('Zato Test CA')
        other_ca = _new_ca('Zato Test Unrelated CA')

        server_names:'list[x509.GeneralName]' = [x509.IPAddress(_loopback_address), x509.DNSName(_localhost_name)]
        mismatch_names:'list[x509.GeneralName]' = [x509.DNSName(_mismatch_name)]

        server = _issue(ca, _localhost_name, server_names, False)
        mismatch = _issue(ca, _mismatch_name, mismatch_names, False)

        self._write(self.ca_path, ca.cert_pem)
        self._write(self.other_ca_path, other_ca.cert_pem)
        self._write(self.server_cert_path, server.cert_pem)
        self._write(self.server_key_path, server.key_pem)
        self._write(self.mismatch_cert_path, mismatch.cert_pem)
        self._write(self.mismatch_key_path, mismatch.key_pem)

        # .. and the client side.
        client_ca = _new_ca('Zato Test Client CA')

        client_first = _issue(client_ca, Client_First_Common_Name, [], True)
        client_second = _issue(client_ca, Client_Second_Common_Name, [], True)

        self._write(self.client_ca_path, client_ca.cert_pem)
        self._write(self.client_first_path, client_first.cert_pem + client_first.key_pem)
        self._write(self.client_second_cert_path, client_second.cert_pem)
        self._write(self.client_second_key_path, client_second.key_pem)

# ################################################################################################################################

    def remove(self) -> 'None':
        """ Removes all the files and the directory.
        """
        for name in os.listdir(self.directory):
            path = os.path.join(self.directory, name)
            os.remove(path)

        os.rmdir(self.directory)

# ################################################################################################################################
# ################################################################################################################################
