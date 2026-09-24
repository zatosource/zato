# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ipaddress
import json
import os
import re
import stat
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding, load_pem_private_key, PublicFormat
from cryptography.x509.oid import NameOID

# pytest
import pytest

# requests
import requests

# Zato
from conftest import PebbleCtx
from zato.common.api import Lets_Encrypt
from zato.common.lets_encrypt.client import CertificateNotObtained, obtain
from zato.common.lets_encrypt.config import get_config
from zato.common.lets_encrypt.state import load_status

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import PebbleServer
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How far the actual validity of a certificate may be from the one its profile states, in seconds.
    Validity_Tolerance = 60

    # The issuer of all the certificates Pebble signs.
    Issuer_Prefix = 'Pebble Intermediate CA'

    # A name that never resolves, so that the challenge can never be validated.
    Unresolvable_Host = 'no-such-host.invalid'

    Private_Key_Pattern = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----', re.DOTALL)

    Management_Timeout = 10

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class IssuedCertificate:
    pem: 'str'
    leaf: 'x509.Certificate'
    leaf_pem: 'str'
    dns_names: 'list[str]'
    ip_addresses: 'list[str]'
    validity: 'int'

# ################################################################################################################################
# ################################################################################################################################

def _read_certificate(path:'str') -> 'IssuedCertificate':
    """ Parses the file HAProxy reads and makes sure that its key belongs to its certificate.
    """
    with open(path) as pem_file:
        pem = pem_file.read()

    certificates = x509.load_pem_x509_certificates(pem.encode())
    leaf = certificates[0]

    key_match = ModuleCtx.Private_Key_Pattern.search(pem)
    assert key_match is not None

    private_key = load_pem_private_key(key_match.group(0).encode(), password=None)

    leaf_public_key = leaf.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    key_public_key = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

    assert leaf_public_key == key_public_key

    alt_names = leaf.extensions.get_extension_for_class(x509.SubjectAlternativeName).value

    ip_addresses:'list[str]' = []
    for ip_address in alt_names.get_values_for_type(x509.IPAddress):
        ip_addresses.append(str(ip_address))

    validity = leaf.not_valid_after_utc - leaf.not_valid_before_utc

    out = IssuedCertificate()
    out.pem = pem
    out.leaf = leaf
    out.leaf_pem = leaf.public_bytes(Encoding.PEM).decode()
    out.dns_names = alt_names.get_values_for_type(x509.DNSName)
    out.ip_addresses = ip_addresses
    out.validity = int(validity.total_seconds())

    return out

# ################################################################################################################################

def _assert_issued_by_pebble(certificate:'IssuedCertificate') -> 'None':
    issuer_names = certificate.leaf.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)
    issuer_name = issuer_names[0].value

    assert isinstance(issuer_name, str)
    assert issuer_name.startswith(ModuleCtx.Issuer_Prefix)

# ################################################################################################################################

def _assert_validity(certificate:'IssuedCertificate', expected:'int') -> 'None':
    difference = abs(certificate.validity - expected)
    assert difference <= ModuleCtx.Validity_Tolerance

# ################################################################################################################################

def _request_renewal(pebble_server:'PebbleServer', certificate:'IssuedCertificate') -> 'None':
    """ Tells Pebble to answer the renewal info queries about the certificate with a window that has already passed,
    which is what Let's Encrypt does when it wants its clients to renew ahead of time.
    """
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=2)
    window_end = now - timedelta(hours=1)

    renewal_info = {
        'suggestedWindow': {
            'start': window_start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'end': window_end.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
    }

    request = {
        'Certificate': certificate.leaf_pem,
        'ARIResponse': json.dumps(renewal_info),
    }

    url = pebble_server.management_url + '/set-renewal-info/'

    response = requests.post(url, json=request, verify=pebble_server.ca_file, timeout=ModuleCtx.Management_Timeout)
    response.raise_for_status()

# ################################################################################################################################
# ################################################################################################################################

def test_dns_name(lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)

    is_changed = obtain(config, needs_reload=False)
    assert is_changed

    certificate = _read_certificate(config.paths.user_pem)

    assert certificate.dns_names == [PebbleCtx.Host]
    assert certificate.ip_addresses == []

    _assert_issued_by_pebble(certificate)
    _assert_validity(certificate, PebbleCtx.Default_Validity)

    mode = stat.S_IMODE(os.stat(config.paths.user_pem).st_mode)
    assert mode == 0o600

    status = load_status(config.paths)

    assert status.last_check_utc is not None
    assert status.is_last_check_ok is True
    assert status.last_check_error == ''

# ################################################################################################################################

def test_ip_address(lets_encrypt_environ:'strstrdict') -> 'None':
    _ = lets_encrypt_environ.pop(Lets_Encrypt.Env.Subject_Alt_Name)
    lets_encrypt_environ[Lets_Encrypt.Env.Public_IP] = PebbleCtx.Loopback

    config = get_config(lets_encrypt_environ)

    is_changed = obtain(config, needs_reload=False)
    assert is_changed

    certificate = _read_certificate(config.paths.user_pem)

    assert certificate.dns_names == []
    assert certificate.ip_addresses == [str(ipaddress.ip_address(PebbleCtx.Loopback))]

    _assert_issued_by_pebble(certificate)
    _assert_validity(certificate, PebbleCtx.Short_Lived_Validity)

# ################################################################################################################################

def test_nothing_due(lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)

    _ = obtain(config, needs_reload=False)
    first = _read_certificate(config.paths.user_pem)

    is_changed = obtain(config, needs_reload=False)
    assert not is_changed

    second = _read_certificate(config.paths.user_pem)
    assert second.pem == first.pem

# ################################################################################################################################

def test_renewal(pebble_server:'PebbleServer', lets_encrypt_environ:'strstrdict') -> 'None':
    config = get_config(lets_encrypt_environ)

    _ = obtain(config, needs_reload=False)
    first = _read_certificate(config.paths.user_pem)

    _request_renewal(pebble_server, first)

    is_changed = obtain(config, needs_reload=False)
    assert is_changed

    second = _read_certificate(config.paths.user_pem)

    assert second.leaf.serial_number != first.leaf.serial_number
    assert second.dns_names == [PebbleCtx.Host]

    _assert_issued_by_pebble(second)

# ################################################################################################################################

def test_ip_address_to_dns_name(lets_encrypt_environ:'strstrdict') -> 'None':
    subject_alt_name = lets_encrypt_environ.pop(Lets_Encrypt.Env.Subject_Alt_Name)
    lets_encrypt_environ[Lets_Encrypt.Env.Public_IP] = PebbleCtx.Loopback

    ip_config = get_config(lets_encrypt_environ)
    _ = obtain(ip_config, needs_reload=False)

    # The same data directory is used again, now with a DNS name in the configuration.
    lets_encrypt_environ[Lets_Encrypt.Env.Subject_Alt_Name] = subject_alt_name
    dns_config = get_config(lets_encrypt_environ)

    is_changed = obtain(dns_config, needs_reload=False)
    assert is_changed

    certificate = _read_certificate(dns_config.paths.user_pem)

    assert certificate.dns_names == [PebbleCtx.Host]
    assert certificate.ip_addresses == []

    _assert_validity(certificate, PebbleCtx.Default_Validity)

# ################################################################################################################################

def test_validation_fails(lets_encrypt_environ:'strstrdict') -> 'None':
    lets_encrypt_environ[Lets_Encrypt.Env.Subject_Alt_Name] = f'subjectAltName=DNS:{ModuleCtx.Unresolvable_Host}'

    config = get_config(lets_encrypt_environ)

    with pytest.raises(CertificateNotObtained, match='could not be obtained'):
        _ = obtain(config, needs_reload=False)

    assert not os.path.exists(config.paths.user_pem)

    status = load_status(config.paths)

    assert status.last_check_utc is not None
    assert status.is_last_check_ok is False
    assert ModuleCtx.Unresolvable_Host in status.last_check_error

# ################################################################################################################################
# ################################################################################################################################
