# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# Zato
from zato.common.as2.partnership import CertificateEntry

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

Sender_Identifier   = 'ZatoRetail'
Receiver_Identifier = 'PartnerCorp'

# The moment all the window checks run against. The entries carry certificates issued by the
# fixtures relative to the current time, and an entry is in service only when the certificate's
# own dates cover the moment too, so the reference moment has to be the current one rather than
# a date typed out here.
Now = datetime.now(timezone.utc)

One_Day = timedelta(days=1)

# ################################################################################################################################
# ################################################################################################################################

def certificate_to_pem(certificate:'any_') -> 'any_':
    """ One certificate in the PEM form the partner form stores it in.
    """
    certificate_bytes = certificate.public_bytes(Encoding.PEM)

    out = certificate_bytes.decode('ascii')
    return out

# ################################################################################################################################

def make_entry(certificate:'any_', valid_from:'any_' = None, valid_until:'any_' = None) -> 'any_':
    """ One rotation list entry, with the configured window the operator declared it under.
    """
    out = CertificateEntry()

    out.certificate = certificate
    out.valid_from = valid_from
    out.valid_until = valid_until

    return out

# ################################################################################################################################

def partnership_config() -> 'stranydict':
    """ The flat configuration dict of one Dashboard-managed AS2 connection,
    with every field of the connection schema present.
    """
    out = {
        'as2_from': Sender_Identifier,
        'as2_to': Receiver_Identifier,

        'isa_qualifier': '',
        'isa_id': '',
        'gs_id': '',
        'unb_id': '',

        'endpoint_url': 'https://partnercorp.example.com/as2',
        'sign_algorithm': '',
        'encryption_algorithm': '',
        'mdn_mode': '',
        'async_mdn_url': '',
        'subject': '',
        'content_type': '',
        'as2_version': '',
        'content_transfer_encoding': '',
        'http_transfer_mode': '',
        'inbound_topic': '',
        'inbound_service': '',

        'sign': True,
        'encrypt': True,
        'compress': False,
        'compress_before_signing': True,
        'mdn_signed': True,
        'preserve_filename': False,
        'verify_tls': True,
        'force_base64': False,
        'prevent_canonicalization': False,
        'warn_on_duplicate_filename': False,
        'is_audit_log_active': True,

        'http_timeout_seconds': 0,
        'chunked_threshold_bytes': 0,
        'ack_overdue_after': 0,
        'resend_max_retries': 0,

        'as2_partner_cert': '',
        'as2_partner_next_cert': '',
        'as2_partner_next_cert_from': '',
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
