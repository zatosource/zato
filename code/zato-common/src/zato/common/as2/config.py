# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# Zato
from zato.common.as2.common import AS2Exception
from zato.common.as2.partnership import CertificateEntry, new_partnership
from zato.common.util.xml_.keystore import DecryptionEntry, load_certificates_pem, load_private_key_pem, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.partnership import Partnership, partnership_list
    from zato.common.typing_ import callable_, dictlist, dtnone, stranydict
    from zato.common.util.xml_.keystore import Keystore
    callable_ = callable_
    dictlist = dictlist
    dtnone = dtnone
    partnership_list = partnership_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# Partnership fields settable directly from configuration, grouped by type -
# the names are the same as the fields of the Partnership dataclass.
partnership_string_fields = ('as2_from', 'as2_to', 'isa_qualifier', 'isa_id', 'gs_id', 'unb_id', 'endpoint_url',
    'sign_algorithm', 'encryption_algorithm', 'mdn_mode', 'async_mdn_url', 'subject', 'content_type', 'as2_version',
    'content_transfer_encoding', 'http_transfer_mode', 'inbound_topic', 'inbound_service')

partnership_bool_fields = ('sign', 'encrypt', 'compress', 'compress_before_signing', 'mdn_signed',
    'preserve_filename', 'verify_tls', 'force_base64', 'prevent_canonicalization', 'warn_on_duplicate_filename')

partnership_int_fields = ('http_timeout_seconds', 'chunked_threshold_bytes', 'ack_overdue_after', 'resend_max_retries')

# The certificate rotation fields of one partner - the current certificate, pasted as PEM,
# plus the optional next-certificate with its activation date for overlap-window rotation.
partnership_certificate_fields = ('as2_partner_cert', 'as2_partner_next_cert', 'as2_partner_next_cert_from')

# ################################################################################################################################
# ################################################################################################################################

def _parse_activation_date(value:'str') -> 'datetime':
    """ Parses an ISO 8601 activation date, taking a date without a timezone to be UTC.
    """
    out = datetime.fromisoformat(value)

    if out.tzinfo is None:
        out = out.replace(tzinfo=timezone.utc)

    return out

# ################################################################################################################################

def _add_certificate_entries(partnership:'Partnership', pem:'str', valid_from:'dtnone') -> 'None':
    """ Adds each certificate of a PEM string to the partner's rotation lists. The same partner
    certificate serves both signature verification and encryption, so each entry joins both lists.
    """
    pem_bytes = pem.encode('utf8')
    certificates = load_certificates_pem(pem_bytes)

    for certificate in certificates:

        entry = CertificateEntry()
        entry.certificate = certificate
        entry.valid_from = valid_from

        partnership.verification_certificates.append(entry)
        partnership.encryption_certificates.append(entry)

# ################################################################################################################################
# ################################################################################################################################

def build_keystore(config:'stranydict', decrypt_func:'callable_') -> 'Keystore':
    """ Builds a keystore out of configuration whose entries are pasted PEM strings,
    with the private keys stored encrypted at rest.
    """

    # Our response to produce
    out = new_keystore()

    signing_key = config['as2_signing_key']
    signing_cert_chain = config['as2_signing_cert_chain']

    # Signing material is the only part that is strictly required.
    if not signing_key:
        raise AS2Exception('No signing key is configured for this AS2 channel or connection')

    if not signing_cert_chain:
        raise AS2Exception('No signing certificate chain is configured for this AS2 channel or connection')

    signing_key = decrypt_func(signing_key)
    signing_key_bytes = signing_key.encode('utf8')
    signing_cert_chain_bytes = signing_cert_chain.encode('utf8')

    out.signing_key = load_private_key_pem(signing_key_bytes)
    out.signing_certificate_chain = load_certificates_pem(signing_cert_chain_bytes)

    if value := config['as2_decryption_key']:
        value = decrypt_func(value)
        value_bytes = value.encode('utf8')
        out.decryption_key = load_private_key_pem(value_bytes)

    # The next-decryption pair joins the rotation entries with no window - during a rotation
    # of our own key, messages encrypted to either the old or the new certificate must decrypt.
    if value := config['as2_next_decryption_key']:

        certificate_pem = config['as2_next_decryption_cert']

        if not certificate_pem:
            raise AS2Exception('A next decryption key requires its certificate for recipient matching')

        value = decrypt_func(value)
        certificate_pem_bytes = certificate_pem.encode('utf8')
        certificates = load_certificates_pem(certificate_pem_bytes)

        value_bytes = value.encode('utf8')

        entry = DecryptionEntry()
        entry.key = load_private_key_pem(value_bytes)
        entry.certificate = certificates[0]

        out.decryption_entries.append(entry)

    if value := config['as2_peer_signing_cert']:
        value_bytes = value.encode('utf8')
        certificates = load_certificates_pem(value_bytes)
        out.peer_signing_certificate = certificates[0]

    if value := config['as2_peer_encryption_cert']:
        value_bytes = value.encode('utf8')
        certificates = load_certificates_pem(value_bytes)
        out.peer_encryption_certificate = certificates[0]

    if value := config['as2_trust_anchors']:
        value_bytes = value.encode('utf8')
        out.trust_anchors = load_certificates_pem(value_bytes)

    return out

# ################################################################################################################################

def build_partnership(config:'stranydict') -> 'Partnership':
    """ Builds one partnership out of flat configuration - the shape one Dashboard-managed
    AS2 connection stores its type-specific fields in.
    """

    # Our response to produce
    out = new_partnership()

    # An empty string means the partnership's own default stays in place ..
    for name in partnership_string_fields:
        if value := config[name]:
            setattr(out, name, value)

    # .. boolean toggles are always taken as configured ..
    for name in partnership_bool_fields:
        setattr(out, name, config[name])

    # .. a zero means the numeric default stays in place ..
    for name in partnership_int_fields:
        if value := config[name]:
            setattr(out, name, value)

    # .. the partner's current certificate has always been active ..
    if value := config['as2_partner_cert']:
        _add_certificate_entries(out, value, None)

    # .. and the optional next-certificate joins the rotation lists,
    # accepted from its activation date on, or immediately when there is none.
    if value := config['as2_partner_next_cert']:

        if activation := config['as2_partner_next_cert_from']:
            valid_from = _parse_activation_date(activation)
        else:
            valid_from = None

        _add_certificate_entries(out, value, valid_from)

    return out

# ################################################################################################################################

def build_partnerships(configs:'dictlist') -> 'partnership_list':
    """ Builds the full list of partnerships out of an iterable of flat configuration dicts.
    """

    # Our response to produce
    out:'partnership_list' = []

    for config in configs:
        partnership = build_partnership(config)
        out.append(partnership)

    return out

# ################################################################################################################################
# ################################################################################################################################
