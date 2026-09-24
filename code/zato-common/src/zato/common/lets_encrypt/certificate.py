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

# Zato
from zato.common.api import Lets_Encrypt

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.lets_encrypt.paths import SSLPaths
    from zato.common.typing_ import anydict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class CertificateInfo:

    # Whether the certificate is the user's own, one from Let's Encrypt or the generated one.
    source: 'str'

    # The DNS names and IP addresses the certificate is for.
    names: 'strlist'

    # Who signed the certificate.
    issuer: 'str'

    # When the certificate expires, in ISO 8601 and UTC.
    not_after_utc: 'str'

    def to_dict(self) -> 'anydict':
        out = {
            'source': self.source,
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

def _is_same_file(path:'str', pem:'str') -> 'bool':
    """ Returns whether a file exists and holds the same certificate as the one given on input.
    """
    if not os.path.exists(path):
        return False

    out = _read_file(path) == pem
    return out

# ################################################################################################################################

def get_in_use_path(paths:'SSLPaths') -> 'strnone':
    """ Returns the file HAProxy presents the certificate from, which is the generated one only if there is no other.
    """
    if os.path.exists(paths.user_pem):
        out = paths.user_pem
    elif os.path.exists(paths.auto_pem):
        out = paths.auto_pem
    else:
        out = None

    return out

# ################################################################################################################################

def get_source(paths:'SSLPaths', pem:'str') -> 'str':
    """ Returns where the certificate HAProxy presents comes from, by comparing it with each of the possible sources.
    """
    if _is_same_file(paths.own_pem, pem):
        out = Lets_Encrypt.Source.Own
    elif _is_same_file(paths.lego_pem, pem):
        out = Lets_Encrypt.Source.Lets_Encrypt
    else:
        out = Lets_Encrypt.Source.Generated

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
    """ Returns details of the certificate HAProxy presents, or None if there is no certificate at all.
    """
    path = get_in_use_path(paths)

    if path is None:
        return None

    pem = _read_file(path)

    # The file also holds the private key and possibly the issuer's certificate, and the first certificate is the server's.
    certificates = x509.load_pem_x509_certificates(pem.encode())
    certificate = certificates[0]

    out = CertificateInfo()
    out.source = get_source(paths, pem)
    out.names = _get_names(certificate)
    out.issuer = _get_issuer(certificate)
    out.not_after_utc = certificate.not_valid_after_utc.isoformat()

    return out

# ################################################################################################################################
# ################################################################################################################################
