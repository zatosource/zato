# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import AS4
from zato.common.as4.common import AS4Exception
from zato.common.as4.profiles import new_edelivery1_pmode, new_edelivery2_pmode, new_ics2_pmode, new_peppol_pmode
from zato.common.util.xml_.constants import TokenType
from zato.common.util.xml_.keystore import load_certificates_pem, load_private_key_pem, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Callable
    from zato.common.as4.pmode import PMode
    from zato.common.typing_ import callable_, stranydict
    from zato.common.util.xml_.keystore import Keystore
    callable_ = callable_
    stranydict = stranydict

    # What the keys stored encrypted at rest are decrypted with
    decryptfunc = Callable[[str], str]

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

# Maps the token type a connection selects in the Dashboard to the WS-Security profile identifier
# that goes on the wire for it.
token_types = {
    AS4.TokenType.X509v3:  TokenType.X509v3,
    AS4.TokenType.PKIPath: TokenType.PKIPath,
    AS4.TokenType.SAML20:  TokenType.SAML20,
}

# ################################################################################################################################
# ################################################################################################################################

def build_keystore(config:'stranydict', decrypt_func:'decryptfunc') -> 'Keystore':
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
    signing_key = signing_key.encode('utf8')
    out.signing_key = load_private_key_pem(signing_key)

    signing_cert_chain = signing_cert_chain.encode('utf8')
    out.signing_certificate_chain = load_certificates_pem(signing_cert_chain)

    if value := config['as4_decryption_key']:
        value = decrypt_func(value)
        value = value.encode('utf8')
        out.decryption_key = load_private_key_pem(value)

    if value := config['as4_peer_signing_cert']:
        value = value.encode('utf8')
        certificates = load_certificates_pem(value)
        out.peer_signing_certificate = certificates[0]

    if value := config['as4_peer_encryption_cert']:
        value = value.encode('utf8')
        certificates = load_certificates_pem(value)
        out.peer_encryption_certificate = certificates[0]

    if value := config['as4_trust_anchors']:
        value = value.encode('utf8')
        out.trust_anchors = load_certificates_pem(value)

    # The assertion a security token service issued, for the exchanges whose token is one of those
    # rather than a certificate travelling as a binary token.
    if value := get_text_field(config, 'as4_saml_assertion'):
        out.saml_assertion = value.encode('utf8')

    return out

# ################################################################################################################################

def build_pmode(config:'stranydict') -> 'PMode':
    """ Builds one P-Mode out of flat configuration, starting from the preset
    matching the configured profile.
    """
    profile = config['as4_profile']
    preset = profile_presets[profile]

    # Our response to produce
    out = preset()

    if value := config['as4_service']:
        out.service = value

    if value := config['as4_action']:
        out.action = value

    if value := config['as4_agreement']:
        out.agreement = value

    if value := config['as4_mpc']:
        out.mpc = value

    if value := config['as4_original_sender']:
        out.original_sender = value

    if value := config['as4_final_recipient']:
        out.final_recipient = value

    if value := config['as4_from_party']:
        out.initiator.party_id = value

    if value := config['as4_to_party']:
        out.responder.party_id = value

    # How the signing certificate travels, when the exchange uses something else than what the
    # profile preset prescribes - the whole chain, or a SAML assertion in place of a certificate.
    if value := get_text_field(config, 'as4_token_type'):
        out.security.token_type = token_types[value]

        # A signature keyed by an assertion has nothing to key it with unless one was configured,
        # and the first message that cannot be built is a late place to find that out.
        if value == AS4.TokenType.SAML20:
            if not get_text_field(config, 'as4_saml_assertion'):
                raise AS4Exception('Token type SAML needs a SAML assertion to be configured too')

    return out

# ################################################################################################################################

def get_text_field(config:'stranydict', name:'str') -> 'str':
    """ Returns one text field of a stored AS4 configuration, or an empty string for a connection
    saved without it - the opaque attributes hold only what was saved, and a column that was saved
    empty genuinely holds a null.
    """
    value = config.get(name)

    if value is None:
        value = ''

    out = value
    return out

# ################################################################################################################################

def get_numeric_field(config:'stranydict', name:'str') -> 'int':
    """ Returns one numeric field of a stored AS4 configuration, or zero for a connection saved
    without it - the opaque attributes of a connection hold only what was saved on it, and zero is
    what an unset field reads as everywhere one is used.

    A config event published by an edit in the Dashboard carries the raw form value, which is text.
    """
    value = config.get(name)

    if not value:
        out = 0

    elif isinstance(value, str):
        out = int(value)

    else:
        out = value

    return out

# ################################################################################################################################

def apply_reception_awareness(pmode:'PMode', config:'stranydict') -> 'None':
    """ Overlays on one P-Mode the reception awareness parameters an outgoing connection configures,
    leaving the profile preset's own value in place for each parameter left empty.
    """
    awareness = pmode.reception_awareness

    if value := get_numeric_field(config, 'as4_retry_max_attempts'):
        awareness.retry_max_attempts = value

    if value := get_numeric_field(config, 'as4_retry_interval'):
        awareness.retry_interval_seconds = value

    if value := get_numeric_field(config, 'as4_missing_receipt_after'):
        awareness.missing_receipt_seconds = value

    # A single permitted attempt is how a connection says its messages go out once and are not
    # repeated, so there is no separate switch for it to contradict.
    awareness.retry = awareness.retry_max_attempts > 1

# ################################################################################################################################

def apply_credentials(pmode:'PMode', config:'stranydict', decrypt_func:'callable_') -> 'None':
    """ Overlays on one P-Mode the credentials an exchange carries next to its signature, for the
    networks that ask for them. The password is stored encrypted, so it is decrypted here, at the
    same point the private keys of a keystore are.
    """
    username = get_text_field(config, 'as4_username')

    if not username:
        return

    pmode.security.username_token_username = username

    if value := get_text_field(config, 'as4_password'):
        pmode.security.username_token_password = decrypt_func(value)

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
