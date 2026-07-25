# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import CertificateBuilder, Name, NameAttribute, random_serial_number
from cryptography.x509.oid import NameOID

# Zato
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# The reconciliation store all the tests write to and the sweep reads from.
Server_Name = 'test-server'

# The identities of both sides
AS2_From = 'ZatoRetail'
AS2_To   = 'PartnerCorp'
Pair     = f'{AS2_From}:{AS2_To}'

# The X12 identifiers of both sides
Our_ISA_ID     = 'ZATORETAIL'
Partner_ISA_ID = 'PARTNERCORP'
X12_Pair       = f'{Our_ISA_ID}:{Partner_ISA_ID}'

# RSA parameters for throwaway test keys.
_rsa_public_exponent = 65537
_rsa_key_size = 2048

# The common name every throwaway certificate is issued to.
_certificate_common_name = 'alerting-test'

# ################################################################################################################################
# ################################################################################################################################

def new_config(**overrides:'any_') -> 'any_':
    """ One partner's connection configuration, the way the alerting sweep sees it.
    """
    out = Bunch()

    out['name'] = 'PartnerCorp AS2'
    out['as2_from'] = AS2_From
    out['as2_to'] = AS2_To
    out['isa_id'] = Partner_ISA_ID
    out['ack_overdue_after'] = 0
    out['alerting_opt_out'] = False
    out['ship_notice_window_hours'] = 0
    out['as2_partner_cert'] = ''

    out.update(overrides)

    return out

# ################################################################################################################################

def make_certificate_pem(days_left:'any_') -> 'any_':
    """ Issues one self-signed certificate expiring in the given number of days,
    returned as a PEM string the way the partner form stores it.
    """
    key = generate_private_key(_rsa_public_exponent, _rsa_key_size)

    common_name = NameAttribute(NameOID.COMMON_NAME, _certificate_common_name)
    name = Name([common_name])

    now = datetime.now(timezone.utc)
    valid_from = now - timedelta(days=1)
    valid_until = now + timedelta(days=days_left)

    public_key = key.public_key()
    serial_number = random_serial_number()

    builder = CertificateBuilder()
    builder = builder.subject_name(name)
    builder = builder.issuer_name(name)
    builder = builder.public_key(public_key)
    builder = builder.serial_number(serial_number)
    builder = builder.not_valid_before(valid_from)
    builder = builder.not_valid_after(valid_until)

    digest_algorithm = SHA256()
    certificate = builder.sign(key, digest_algorithm)

    certificate_bytes = certificate.public_bytes(Encoding.PEM)

    out = certificate_bytes.decode('ascii')
    return out

# ################################################################################################################################

def findings_of_kind(findings:'any_', kind:'any_') -> 'anylist':
    """ Filters one sweep's findings down to a single kind - a test seeding
    the store for one check must not trip over the others.
    """
    out = []

    for finding in findings:
        if finding.kind == kind:
            out.append(finding)

    return out

# ################################################################################################################################
# ################################################################################################################################
