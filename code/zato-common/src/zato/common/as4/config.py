# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as4.common import AS4Exception
from zato.common.as4.profiles import new_edelivery1_pmode, new_edelivery2_pmode, new_ics2_pmode, new_peppol_pmode
from zato.common.util.xml_.keystore import load_certificates_pem, load_private_key_pem, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import callable_, stranydict
    from zato.common.util.xml_.keystore import Keystore
    callable_ = callable_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

pmode_list = list['PMode']

# ################################################################################################################################
# ################################################################################################################################

# Maps profile names to their P-Mode presets.
profile_presets = {
    'edelivery1': new_edelivery1_pmode,
    'edelivery2': new_edelivery2_pmode,
    'peppol':     new_peppol_pmode,
    'ics2':       new_ics2_pmode,
}

# P-Mode fields settable directly from configuration.
pmode_string_fields = ('service', 'action', 'agreement', 'mpc', 'original_sender', 'final_recipient')

# ################################################################################################################################
# ################################################################################################################################

def build_keystore(config:'stranydict', decrypt_func:'callable_') -> 'Keystore':
    """ Builds a keystore out of configuration whose entries are pasted PEM strings,
    with the private keys stored encrypted at rest.
    """

    # Our response to produce
    out = new_keystore()

    signing_key = config['as4_signing_key']
    signing_cert_chain = config['as4_signing_cert_chain']

    # Signing material is the only part that is strictly required.
    if not signing_key:
        raise AS4Exception('No signing key is configured for this AS4 connection')

    if not signing_cert_chain:
        raise AS4Exception('No signing certificate chain is configured for this AS4 connection')

    signing_key = decrypt_func(signing_key)
    out.signing_key = load_private_key_pem(signing_key.encode('utf8'))
    out.signing_certificate_chain = load_certificates_pem(signing_cert_chain.encode('utf8'))

    if value := config['as4_decryption_key']:
        value = decrypt_func(value)
        out.decryption_key = load_private_key_pem(value.encode('utf8'))

    if value := config['as4_peer_signing_cert']:
        certificates = load_certificates_pem(value.encode('utf8'))
        out.peer_signing_certificate = certificates[0]

    if value := config['as4_peer_encryption_cert']:
        certificates = load_certificates_pem(value.encode('utf8'))
        out.peer_encryption_certificate = certificates[0]

    if value := config['as4_trust_anchors']:
        out.trust_anchors = load_certificates_pem(value.encode('utf8'))

    return out

# ################################################################################################################################

def build_pmode(config:'stranydict') -> 'PMode':
    """ Builds one P-Mode out of flat configuration, starting from the preset
    matching the configured profile.
    """
    preset = profile_presets[config['as4_profile']]

    # Our response to produce
    out = preset()

    for name in pmode_string_fields:
        if value := config['as4_' + name]:
            setattr(out, name, value)

    if value := config['as4_from_party']:
        out.initiator.party_id = value

    if value := config['as4_to_party']:
        out.responder.party_id = value

    return out

# ################################################################################################################################

def build_pmodes(config:'stranydict') -> 'pmode_list':
    """ Builds the full list of P-Modes for one channel or connection - the main one
    built from the configured fields plus one clone per extra service and action pair.
    """
    main = build_pmode(config)

    # Our response to produce
    out = [main]

    # Each extra line names one more service and action pair served
    # under otherwise the same P-Mode parameters. The opaque column genuinely
    # stores a null when the channel was saved without any extra pairs.
    extra_pmodes = config['as4_extra_pmodes']
    if extra_pmodes is None:
        extra_pmodes = ''

    for line in extra_pmodes.splitlines():

        line = line.strip()
        if not line:
            continue

        service, _, action = line.partition('|')

        pmode = build_pmode(config)
        pmode.service = service.strip()
        pmode.action = action.strip()

        out.append(pmode)

    return out

# ################################################################################################################################
# ################################################################################################################################
