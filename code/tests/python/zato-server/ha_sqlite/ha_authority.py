# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The certificates of an active-standby pair - one authority that issues the certificate of each node for the mutual TLS
# of the replication link, each valid for the name and the address it serves under.

# stdlib
import ipaddress
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
    from zato.common.typing_ import strlist

    # Dummy assignments to satisfy type checkers
    EllipticCurvePrivateKey = EllipticCurvePrivateKey
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long each certificate is valid, in days
    Validity_Days = 30

    # How far back each certificate is valid from, to tolerate a clock that a fault moves backwards, in days
    Backdate_Days = 1

    # The common name of the authority
    Authority_Name = 'Zato HA Test Authority'

    # The file names of the authority
    Authority_Cert_File = 'ca.pem'
    Authority_Key_File = 'ca.key'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class IssuedCertificate:
    """ The files of one certificate and its private key.
    """
    cert_path: 'str'
    key_path: 'str'

# ################################################################################################################################
# ################################################################################################################################

def _new_key() -> 'EllipticCurvePrivateKey':
    out = ec.generate_private_key(ec.SECP256R1())
    return out

# ################################################################################################################################

def _write_key(key:'EllipticCurvePrivateKey', path:'str') -> 'None':
    encoded = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with open(path, 'wb') as key_file:
        _ = key_file.write(encoded)

    os.chmod(path, 0o600)

# ################################################################################################################################

def _write_cert(cert:'x509.Certificate', path:'str') -> 'None':
    encoded = cert.public_bytes(serialization.Encoding.PEM)

    with open(path, 'wb') as cert_file:
        _ = cert_file.write(encoded)

# ################################################################################################################################

def _validity() -> 'tuple[datetime, datetime]':
    now = datetime.now(timezone.utc)
    not_before = now - timedelta(days=ModuleCtx.Backdate_Days)
    not_after = now + timedelta(days=ModuleCtx.Validity_Days)

    out = not_before, not_after
    return out

# ################################################################################################################################
# ################################################################################################################################

class Authority:
    """ The authority of one test run, which issues every certificate of the pair.
    """

    def __init__(self, directory:'str') -> 'None':
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

        self.key = _new_key()
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ModuleCtx.Authority_Name)])
        not_before, not_after = _validity()
        public_key = self.key.public_key()
        basic_constraints = x509.BasicConstraints(ca=True, path_length=0)

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(name)
        builder = builder.issuer_name(name)
        builder = builder.public_key(public_key)
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.not_valid_before(not_before)
        builder = builder.not_valid_after(not_after)
        builder = builder.add_extension(basic_constraints, critical=True)

        self.cert = builder.sign(self.key, hashes.SHA256())

        self.cert_path = os.path.join(directory, ModuleCtx.Authority_Cert_File)
        _write_cert(self.cert, self.cert_path)
        _write_key(self.key, os.path.join(directory, ModuleCtx.Authority_Key_File))

# ################################################################################################################################

    def issue(self, name:'str', dns_names:'strlist', ip_addresses:'strlist') -> 'IssuedCertificate':
        """ Issues a certificate for both ends of a TLS connection, valid for the given names and addresses.
        """
        key = _new_key()
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, name)])
        not_before, not_after = _validity()
        public_key = key.public_key()

        alternative_names:'list[x509.GeneralName]' = []

        for dns_name in dns_names:
            alternative_names.append(x509.DNSName(dns_name))

        for ip_address in ip_addresses:
            address = ipaddress.ip_address(ip_address)
            alternative_names.append(x509.IPAddress(address))

        subject_alternative_name = x509.SubjectAlternativeName(alternative_names)
        extended_key_usage = x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH, ExtendedKeyUsageOID.CLIENT_AUTH])
        basic_constraints = x509.BasicConstraints(ca=False, path_length=None)

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(subject)
        builder = builder.issuer_name(self.cert.subject)
        builder = builder.public_key(public_key)
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.not_valid_before(not_before)
        builder = builder.not_valid_after(not_after)
        builder = builder.add_extension(subject_alternative_name, critical=False)
        builder = builder.add_extension(extended_key_usage, critical=False)
        builder = builder.add_extension(basic_constraints, critical=True)

        cert = builder.sign(self.key, hashes.SHA256())

        out = IssuedCertificate()
        out.cert_path = os.path.join(self.directory, f'{name}.pem')
        out.key_path = os.path.join(self.directory, f'{name}.key')

        _write_cert(cert, out.cert_path)
        _write_key(key, out.key_path)

        return out

# ################################################################################################################################
# ################################################################################################################################
