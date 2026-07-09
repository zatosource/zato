# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.common import AS2Exception
from zato.common.as2.partnership import new_partnership
from zato.common.util.xml_.keystore import load_certificates_pem, load_private_key_pem, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.partnership import Partnership, partnership_list
    from zato.common.typing_ import callable_, dictlist, stranydict
    from zato.common.util.xml_.keystore import Keystore
    callable_ = callable_
    dictlist = dictlist
    partnership_list = partnership_list
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# Partnership fields settable directly from configuration, grouped by type -
# the names are the same as the fields of the Partnership dataclass.
partnership_string_fields = ('as2_from', 'as2_to', 'endpoint_url', 'sign_algorithm', 'encryption_algorithm',
    'mdn_mode', 'async_mdn_url', 'subject', 'content_type', 'as2_version', 'content_transfer_encoding',
    'http_transfer_mode', 'inbound_topic', 'inbound_service')

partnership_bool_fields = ('sign', 'encrypt', 'compress', 'compress_before_signing', 'mdn_signed',
    'preserve_filename', 'verify_tls', 'force_base64', 'prevent_canonicalization', 'warn_on_duplicate_filename')

partnership_int_fields = ('http_timeout_seconds', 'chunked_threshold_bytes', 'ack_overdue_after', 'resend_max_retries')

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
    out.signing_key = load_private_key_pem(signing_key.encode('utf8'))
    out.signing_certificate_chain = load_certificates_pem(signing_cert_chain.encode('utf8'))

    if value := config['as2_decryption_key']:
        value = decrypt_func(value)
        out.decryption_key = load_private_key_pem(value.encode('utf8'))

    if value := config['as2_peer_signing_cert']:
        certificates = load_certificates_pem(value.encode('utf8'))
        out.peer_signing_certificate = certificates[0]

    if value := config['as2_peer_encryption_cert']:
        certificates = load_certificates_pem(value.encode('utf8'))
        out.peer_encryption_certificate = certificates[0]

    if value := config['as2_trust_anchors']:
        out.trust_anchors = load_certificates_pem(value.encode('utf8'))

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

    # .. and a zero means the numeric default stays in place.
    for name in partnership_int_fields:
        if value := config[name]:
            setattr(out, name, value)

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
