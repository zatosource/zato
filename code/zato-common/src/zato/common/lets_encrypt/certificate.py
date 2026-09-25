# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# cryptography
from cryptography import x509
from cryptography.x509.oid import NameOID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.lets_encrypt.paths import SSLPaths
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CertificateInfo:

    # The DNS names and IP addresses the certificate is for.
    names: 'strlist'

    # Who signed the certificate.
    issuer: 'str'

    # When the certificate expires, in ISO 8601 and UTC.
    not_after_utc: 'str'

    def to_dict(self) -> 'anydict':
        out = {
            'names': self.names,
            'issuer': self.issuer,
            'not_after_utc': self.not_after_utc,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

def _read_file(path:'str') -> 'str':
    with open(path) as input_file:
        out = input_file.read()
    return out

# ################################################################################################################################

def _get_issuer(certificate:'x509.Certificate') -> 'str':
    """ Returns the common name of the issuer, or its whole name if it has no common name.
    """
    common_names = certificate.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)

    if common_names:
        out = str(common_names[0].value)
    else:
        out = certificate.issuer.rfc4514_string()

    return out

# ################################################################################################################################

def _get_names(certificate:'x509.Certificate') -> 'strlist':
    """ Returns the DNS names and IP addresses the certificate is for.
    """
    out:'strlist' = []

    try:
        extension = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    except x509.ExtensionNotFound:
        return out

    for dns_name in extension.value.get_values_for_type(x509.DNSName):
        out.append(dns_name)

    for ip_address in extension.value.get_values_for_type(x509.IPAddress):
        out.append(str(ip_address))

    return out

# ################################################################################################################################

def get_certificate_info(paths:'SSLPaths') -> 'CertificateInfo | None':
    """ Returns details of the certificate obtained from Let's Encrypt, or None if none was obtained yet.
    """
    if not os.path.exists(paths.lego_pem):
        return None

    pem = _read_file(paths.lego_pem)

    # The file also holds the private key and possibly the issuer's certificate, and the first certificate is the server's.
    certificates = x509.load_pem_x509_certificates(pem.encode())
    certificate = certificates[0]

    out = CertificateInfo()
    out.names = _get_names(certificate)
    out.issuer = _get_issuer(certificate)
    out.not_after_utc = certificate.not_valid_after_utc.isoformat()

    return out

# ################################################################################################################################
# ################################################################################################################################
