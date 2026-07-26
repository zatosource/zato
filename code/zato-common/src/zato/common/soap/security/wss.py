# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path

# Zato
from zato.common.soap.common import NS, SOAPSecurityException
from zato.common.soap.security.saml import add_assertion, add_attribute, get_assertion, new_assertion, sign_assertion, \
    validate_assertion_conditions, verify_assertion
from zato.common.soap.security.usernametoken import add_username_token, verify_username_token
from zato.common.soap.security.x509 import decrypt_body, encrypt_body, sign, verify, VerifiedSignature
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.keystore import load_certificates_pem, load_private_key_pem, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    from zato.common.util.xml_.keystore import Keystore
    any_ = any_
    anydict = anydict
    Keystore = Keystore
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class Mode:
    """ The modes a WS-Security definition can be in - which credential scheme
    the definition carries.
    """
    UsernameToken = 'username_token'
    X509 = 'x509'
    SAML = 'saml'

# All the modes a definition may use, in the order the Dashboard shows them.
All_Modes = (Mode.UsernameToken, Mode.X509, Mode.SAML)

# ################################################################################################################################
# ################################################################################################################################

# The keystores built so far, keyed by what identifies a definition's trust material. Entries are
# dropped when a definition is edited or deleted, so this grows with the number of definitions
# rather than with traffic.
_keystore_cache:'anydict' = {}

# What a definition that does not say so is taken to mean. All three are optional inputs stored in a
# definition's opaque attributes, so a definition that never set one simply has no such key - the
# dashboard always sends all three as real booleans, but an enmasse YAML definition carries only the
# keys it was written with, and reading them directly turned a plaintext-password definition without
# a use_digest line into a KeyError on every request, which surfaced to the caller as a 500 rather
# than as an authentication result.
#
# False is what the absence means in each case rather than a lenient guess. The UsernameToken profile
# reads an absent password type as clear text, and a definition that does not ask for a signature or
# for encryption has not configured anything for these to skip - a definition that does ask and has
# nothing to verify against still fails closed, in validate_certificate_chain.
Default_Use_Digest = False
Default_Sign = False
Default_Encrypt = False

# What an X.509 definition that asks for neither a signature nor encryption is told, both when it is
# saved and if one already saved is met on the message path.
No_X509_Operation_Message = 'An X.509 definition needs signing, encryption or both'

# ################################################################################################################################
# ################################################################################################################################

def keystore_from_config(config:'stranydict') -> 'Keystore':
    """ Builds a keystore out of the PEM files a WS-Security definition points to. This reads
    from disk and parses private keys, so callers on the message path use get_keystore instead.
    """

    # Our response to produce
    out = new_keystore()

    # Our own signing key with its certificate chain ..
    if signing_key_path := config.get('signing_key'):
        pem_data = Path(signing_key_path).read_bytes()
        out.signing_key = load_private_key_pem(pem_data)

    if signing_certificate_chain_path := config.get('signing_certificate_chain'):
        pem_data = Path(signing_certificate_chain_path).read_bytes()
        out.signing_certificate_chain = load_certificates_pem(pem_data)

    # .. our own decryption key - with RSA it is usually the signing key again
    # .. but a definition may keep a separate one ..
    if decryption_key_path := config.get('decryption_key'):
        pem_data = Path(decryption_key_path).read_bytes()
        out.decryption_key = load_private_key_pem(pem_data)

    # .. the other side's certificate, used both to encrypt to them and to pin their signatures ..
    if peer_certificate_path := config.get('peer_certificate'):
        pem_data = Path(peer_certificate_path).read_bytes()
        certificates = load_certificates_pem(pem_data)
        peer = certificates[0]
        out.peer_encryption_certificate = peer
        out.peer_signing_certificate = peer

    # .. and the CA certificates their signing certificates may chain up to instead of pinning.
    if trust_anchors_path := config.get('trust_anchors'):
        pem_data = Path(trust_anchors_path).read_bytes()
        out.trust_anchors = load_certificates_pem(pem_data)

    return out

# ################################################################################################################################

def _keystore_cache_key(config:'stranydict') -> 'tuple':
    """ The identity of the trust material a definition points at. The definition's id alone would
    not do, because a definition may be edited to point at different files, and the paths alone
    would not do either, because two definitions may share a file yet differ in what they do
    with it - so the key is both.
    """
    out = (
        config.get('id'),
        config.get('signing_key'),
        config.get('signing_certificate_chain'),
        config.get('decryption_key'),
        config.get('peer_certificate'),
        config.get('trust_anchors'),
    )

    return out

# ################################################################################################################################

def get_keystore(config:'stranydict') -> 'Keystore':
    """ Returns the keystore of a definition, building it on first use and reusing it afterwards.

    Building a keystore means blocking disk reads and an RSA private key parse. Doing that per
    message was the single most expensive thing on this path, and under gevent the disk read
    blocks the whole worker rather than just the greenlet doing it.
    """
    key = _keystore_cache_key(config)

    if key in _keystore_cache:
        out = _keystore_cache[key]
    else:
        out = keystore_from_config(config)
        _keystore_cache[key] = out

    return out

# ################################################################################################################################

def invalidate_keystores(definition_id:'any_') -> 'None':
    """ Forgets the keystores of one definition, which is what an edit or a delete calls for -
    the files a definition points at may have been replaced without their paths changing.
    """
    for key in list(_keystore_cache):
        if key[0] == definition_id:
            del _keystore_cache[key]

# ################################################################################################################################
# ################################################################################################################################

def _flag(config:'stranydict', name:'str', default:'bool') -> 'bool':
    """ Returns one of a definition's optional boolean flags, or what its absence means.
    """
    out = config.get(name)

    if out is None:
        out = default

    return out

# ################################################################################################################################

def _apply_username_token(envelope:'any_', config:'stranydict') -> 'None':
    """ Adds a UsernameToken with the definition's credentials, in clear text or digest form.
    """
    use_digest = _flag(config, 'use_digest', Default_Use_Digest)

    _ = add_username_token(envelope, config['username'], config['password'], use_digest)

# ################################################################################################################################

def _apply_x509(envelope:'any_', config:'stranydict') -> 'None':
    """ Signs the envelope and encrypts its body, each when the definition calls for it.
    """
    keystore = get_keystore(config)

    # Signing comes first so the signature covers the plaintext body ..
    if _flag(config, 'sign', Default_Sign):
        _ = sign(envelope, keystore)

    # .. and only then does the body turn into ciphertext.
    if _flag(config, 'encrypt', Default_Encrypt):
        encrypt_body(envelope, keystore)

# ################################################################################################################################

def _apply_saml(envelope:'any_', config:'stranydict') -> 'None':
    """ Builds a sender-vouches assertion out of the definition and places it in the security header,
    signing it first when the definition calls for it - which is what XUA-based exchanges require.
    """
    audience = config.get('audience')
    assertion = new_assertion(config['issuer'], config['subject'], audience)

    # Role and organization details travel as assertion attributes.
    if attributes := config.get('attributes'):
        for name, value in attributes.items():
            add_attribute(assertion, name, value)

    # A signed assertion is signed before it enters the header so the signature covers its final form.
    if _flag(config, 'sign', Default_Sign):
        keystore = get_keystore(config)
        _ = sign_assertion(assertion, keystore)

    add_assertion(envelope, assertion)

# ################################################################################################################################
# ################################################################################################################################

def _enforce_username_token(envelope:'any_', config:'stranydict') -> 'VerifiedSignature | None':
    """ Checks the incoming UsernameToken against the definition's credentials, in the password
    form the definition configured.
    """
    use_digest = _flag(config, 'use_digest', Default_Use_Digest)

    verify_username_token(envelope, config['username'], config['password'], use_digest)

    # A UsernameToken proves who the caller is, it does not sign anything.
    return None

# ################################################################################################################################

def _enforce_x509(envelope:'any_', config:'stranydict') -> 'VerifiedSignature | None':
    """ Decrypts the body and verifies the signature, each when the definition calls for it.
    Returns what the signature covered so the caller can bind its own reading of the message to it.
    """
    needs_decryption = _flag(config, 'encrypt', Default_Encrypt)
    needs_signature = _flag(config, 'sign', Default_Sign)

    # A signature and encryption are the two things this mode has, so a definition
    # asking for neither states no requirement for a message to meet.
    if not needs_decryption and not needs_signature:
        raise SOAPSecurityException(No_X509_Operation_Message)

    keystore = get_keystore(config)

    # Decryption comes first so the signature can be checked over the plaintext body ..
    if needs_decryption:
        decrypt_body(envelope, keystore)

    # .. and now that the body is readable, the signature over it can be verified.
    if needs_signature:
        out = verify(envelope, keystore)
    else:
        out = None

    return out

# ################################################################################################################################

def _enforce_saml(envelope:'any_', config:'stranydict') -> 'VerifiedSignature | None':
    """ Checks that the incoming message carries a valid assertion from the expected issuer.

    The issuer is a string the sender writes into the message, so on its own it proves nothing -
    the signature is what ties the assertion to an issuer that actually holds a key we trust.
    """
    assertion = get_assertion(envelope)

    # The signature is checked first. Everything below reads fields out of the assertion, and
    # until the signature verifies none of those fields mean anything - including the issuer.
    keystore = get_keystore(config)
    _ = verify_assertion(assertion, keystore)

    issuer_element = assertion.find(qname(NS.SAML2, 'Issuer'))

    if issuer_element is None:
        raise SOAPSecurityException('SAML assertion has no Issuer')

    if issuer_element.text != config['issuer']:
        raise SOAPSecurityException('SAML issuer does not match')

    validate_assertion_conditions(assertion, config.get('audience'))

    # The assertion's signature covers the assertion, not the body, so there is nothing here for
    # the caller to bind its reading of the message to.
    return None

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

def enforce_wss(envelope:'any_', config:'stranydict') -> 'VerifiedSignature | None':
    """ Enforces a WS-Security definition on an incoming envelope, raising
    SOAPSecurityException when the message does not satisfy the definition's mode. Returns what
    a signature covered, when the definition's mode involves one, so the caller can check that
    the part of the message it goes on to process is the part that was verified.
    """
    mode = config['mode']

    if enforce_func := _enforce_by_mode.get(mode):
        out = enforce_func(envelope, config)

    # .. anything else is not a recognized mode.
    else:
        raise SOAPSecurityException(f'Unknown WS-Security mode `{mode}`')

    return out

# ################################################################################################################################
# ################################################################################################################################
