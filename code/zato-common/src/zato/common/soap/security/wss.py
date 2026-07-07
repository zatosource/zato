# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.soap.common import NS, SOAPSecurityException
from zato.common.soap.security.saml import add_assertion, add_attribute, get_assertion, new_assertion
from zato.common.soap.security.usernametoken import add_username_token, verify_username_token
from zato.common.soap.security.x509 import decrypt_body, encrypt_body, sign, verify
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.keystore import load_certificates_pem, load_private_key_pem, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    Keystore = Keystore
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class Mode:
    """ The modes a WS-Security definition can be in - which one of the report's
    credential schemes the definition carries.
    """
    UsernameToken = 'username_token'
    X509 = 'x509'
    SAML = 'saml'

# All the modes a definition may use, in the order the Dashboard shows them.
All_Modes = (Mode.UsernameToken, Mode.X509, Mode.SAML)

# ################################################################################################################################
# ################################################################################################################################

def keystore_from_config(config:'stranydict') -> 'Keystore':
    """ Builds a keystore out of the PEM material a WS-Security definition holds.
    """

    # Our response to produce
    out = new_keystore()

    # Our own signing key with its certificate chain ..
    if signing_key := config.get('signing_key'):
        out.signing_key = load_private_key_pem(signing_key.encode('utf-8'))

    if signing_certificate_chain := config.get('signing_certificate_chain'):
        out.signing_certificate_chain = load_certificates_pem(signing_certificate_chain.encode('utf-8'))

    # .. our own decryption key - with RSA it is usually the signing key again
    # .. but a definition may keep a separate one ..
    if decryption_key := config.get('decryption_key'):
        out.decryption_key = load_private_key_pem(decryption_key.encode('utf-8'))

    # .. the other side's certificate, used both to encrypt to them and to pin their signatures ..
    if peer_certificate := config.get('peer_certificate'):
        certificates = load_certificates_pem(peer_certificate.encode('utf-8'))
        peer = certificates[0]
        out.peer_encryption_certificate = peer
        out.peer_signing_certificate = peer

    # .. and the CA certificates their signing certificates may chain up to instead of pinning.
    if trust_anchors := config.get('trust_anchors'):
        out.trust_anchors = load_certificates_pem(trust_anchors.encode('utf-8'))

    return out

# ################################################################################################################################
# ################################################################################################################################

def _apply_username_token(envelope:'any_', config:'stranydict') -> 'None':
    """ Adds a UsernameToken with the definition's credentials, in clear text or digest form.
    """
    _ = add_username_token(envelope, config['username'], config['password'], config['use_digest'])

# ################################################################################################################################

def _apply_x509(envelope:'any_', config:'stranydict') -> 'None':
    """ Signs the envelope and encrypts its body, each when the definition calls for it.
    """
    keystore = keystore_from_config(config)

    # Signing comes first so the signature covers the plaintext body ..
    if config['sign']:
        _ = sign(envelope, keystore)

    # .. and only then does the body turn into ciphertext.
    if config['encrypt']:
        encrypt_body(envelope, keystore)

# ################################################################################################################################

def _apply_saml(envelope:'any_', config:'stranydict') -> 'None':
    """ Builds a sender-vouches assertion out of the definition and places it in the security header.
    """
    audience = config.get('audience')
    assertion = new_assertion(config['issuer'], config['subject'], audience)

    # Role and organization details travel as assertion attributes.
    if attributes := config.get('attributes'):
        for name, value in attributes.items():
            add_attribute(assertion, name, value)

    add_assertion(envelope, assertion)

# ################################################################################################################################
# ################################################################################################################################

def _enforce_username_token(envelope:'any_', config:'stranydict') -> 'None':
    """ Checks the incoming UsernameToken against the definition's credentials.
    """
    verify_username_token(envelope, config['username'], config['password'])

# ################################################################################################################################

def _enforce_x509(envelope:'any_', config:'stranydict') -> 'None':
    """ Decrypts the body and verifies the signature, each when the definition calls for it.
    """
    keystore = keystore_from_config(config)

    # Decryption comes first so the signature can be checked over the plaintext body ..
    if config['encrypt']:
        decrypt_body(envelope, keystore)

    # .. and now that the body is readable, the signature over it can be verified.
    if config['sign']:
        _ = verify(envelope, keystore)

# ################################################################################################################################

def _enforce_saml(envelope:'any_', config:'stranydict') -> 'None':
    """ Checks that the incoming message carries an assertion from the expected issuer.
    """
    assertion = get_assertion(envelope)
    issuer_element = assertion.find(qname(NS.SAML2, 'Issuer'))

    if issuer_element is None:
        raise SOAPSecurityException('SAML assertion has no Issuer')

    if issuer_element.text != config['issuer']:
        raise SOAPSecurityException('SAML issuer does not match')

# ################################################################################################################################
# ################################################################################################################################

# What to call to apply each mode to an outgoing envelope.
_apply_by_mode = {
    Mode.UsernameToken: _apply_username_token,
    Mode.X509:          _apply_x509,
    Mode.SAML:          _apply_saml,
}

# What to call to enforce each mode on an incoming envelope.
_enforce_by_mode = {
    Mode.UsernameToken: _enforce_username_token,
    Mode.X509:          _enforce_x509,
    Mode.SAML:          _enforce_saml,
}

# ################################################################################################################################
# ################################################################################################################################

def apply_wss(envelope:'any_', config:'stranydict') -> 'None':
    """ Applies a WS-Security definition to an outgoing envelope - whatever
    the definition's mode calls for ends up in the message's security header.
    """
    mode = config['mode']

    if apply_func := _apply_by_mode.get(mode):
        apply_func(envelope, config)

    # .. anything else is not a recognized mode.
    else:
        raise SOAPSecurityException(f'Unknown WS-Security mode `{mode}`')

# ################################################################################################################################

def enforce_wss(envelope:'any_', config:'stranydict') -> 'None':
    """ Enforces a WS-Security definition on an incoming envelope, raising
    SOAPSecurityException when the message does not satisfy the definition's mode.
    """
    mode = config['mode']

    if enforce_func := _enforce_by_mode.get(mode):
        enforce_func(envelope, config)

    # .. anything else is not a recognized mode.
    else:
        raise SOAPSecurityException(f'Unknown WS-Security mode `{mode}`')

# ################################################################################################################################
# ################################################################################################################################
