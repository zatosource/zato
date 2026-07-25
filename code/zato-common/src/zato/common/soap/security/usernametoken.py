# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from hashlib import sha1

# lxml
from lxml import etree

# Zato
from zato.common.crypto.api import CryptoManager, is_string_equal
from zato.common.soap.common import NS, SOAPSecurityException
from zato.common.soap.envelope import get_security_header
from zato.common.soap.security.replay import replay_cache
from zato.common.util.xml_.core import element_text, from_timestamp, qname, utc_timestamp, XMLException
from zato.common.util.xml_.xmlsec import decode_base64

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The Type attribute values from the UsernameToken profile 1.0.
_password_text   = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
_password_digest = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest'

_nonce_encoding = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary'

# How much randomness goes into a nonce.
_nonce_size_bits = 128

# How long a digest token stays usable after its wsu:Created. This is the window inside which a
# captured token would be accepted if it were not for the nonce cache, so it is deliberately
# short - the profile leaves the value to the receiver.
Created_TTL_Seconds = 300

# How far apart the two peers' clocks may be. Without a window a peer whose clock runs a second
# fast would have every token rejected.
Clock_Skew_Seconds = 60

# What nonces are keyed by in the shared replay cache, so they cannot collide with the assertion
# ids the same cache remembers.
Nonce_Cache_Prefix = 'wsse-nonce:'

# ################################################################################################################################
# ################################################################################################################################

def _compute_digest(nonce:'bytes', created:'str', password:'str') -> 'str':
    """ Computes the password digest from the UsernameToken profile -
    Base64(SHA-1(nonce + created + password)).

    Two properties of this construction are worth being explicit about, because both are the
    profile's and neither is a choice made here.

    SHA-1 is mandatory. The profile names it, so a token computed with anything else is a token no
    conforming receiver will accept, and interoperability is the entire reason for using the digest
    form. It is not a signature and nothing is authenticated by its collision resistance - the nonce
    and the creation time are what keep a captured token from being replayed - but a deployment
    choosing the digest form should know that it is committing to SHA-1 and not to something current.

    Verifying a digest requires the receiver to hold the password in a recoverable form. The digest
    is computed over the password itself, so checking one means computing the same digest, which
    means having the plaintext - a channel configured for digest cannot store a hash of the password
    the way a password store otherwise would. The digest form protects the password in transit, on a
    hop that would otherwise carry it in clear, and it does so at the cost of how the password can
    be kept at rest. Where that trade is the wrong way round, the text form under TLS keeps the
    password out of the receiver's own storage instead.
    """
    digest = sha1(nonce + created.encode('utf-8') + password.encode('utf-8')).digest()

    out = b64encode(digest).decode('ascii')
    return out

# ################################################################################################################################

def add_username_token(envelope:'any_', username:'str', password:'str', use_digest:'bool'=False) -> 'any_':
    """ Adds a wsse:UsernameToken to the security header - with the password either
    in clear text or as the profile's SHA-1 digest with a nonce and a creation time.
    Returns the token element.
    """
    security = get_security_header(envelope)

    token = etree.SubElement(security, qname(NS.WSSE, 'UsernameToken'))

    username_element = etree.SubElement(token, qname(NS.WSSE, 'Username'))
    username_element.text = username

    password_element = etree.SubElement(token, qname(NS.WSSE, 'Password'))

    if use_digest:
        nonce = bytes.fromhex(CryptoManager.generate_hex_string(_nonce_size_bits))
        created = utc_timestamp()

        password_element.set('Type', _password_digest)
        password_element.text = _compute_digest(nonce, created, password)

        nonce_element = etree.SubElement(token, qname(NS.WSSE, 'Nonce'))
        nonce_element.set('EncodingType', _nonce_encoding)
        nonce_element.text = b64encode(nonce).decode('ascii')

        created_element = etree.SubElement(token, qname(NS.WSU, 'Created'))
        created_element.text = created

    else:
        password_element.set('Type', _password_text)
        password_element.text = password

    return token

# ################################################################################################################################

def _verify_digest_password(
    token:'any_',
    password_received:'str',
    expected_password:'str',
    skew_seconds:'int',
    ) -> 'bool':
    """ Recomputes the digest of a UsernameToken from the message's own nonce and creation time
    and reports whether it matches. The nonce and the time are what stop the digest being
    replayable, so both are validated before the digest is believed.
    """
    nonce_element = token.find(qname(NS.WSSE, 'Nonce'))
    created_element = token.find(qname(NS.WSU, 'Created'))

    if nonce_element is None:
        raise SOAPSecurityException('Digest token has no Nonce')

    if created_element is None:
        raise SOAPSecurityException('Digest token has no Created')

    nonce_text = element_text(nonce_element)
    created_text = element_text(created_element)

    # An empty Nonce element carries None rather than text, which decode_base64 cannot take,
    # so it is refused here as the security failure it is rather than surfacing as a TypeError.
    if not nonce_text:
        raise SOAPSecurityException('Digest token has an empty Nonce')

    if not created_text:
        raise SOAPSecurityException('Digest token has an empty Created')

    try:
        nonce = decode_base64(nonce_text)
    except Exception:
        raise SOAPSecurityException('Digest token has a malformed Nonce')

    # The creation time is what bounds how long a captured token stays usable, and the nonce is
    # what stops it being used twice inside that window. Neither works without the other, so both
    # are checked before the digest itself is compared.
    _check_created(created_text, skew_seconds)

    replay_cache.check_and_add(f'{Nonce_Cache_Prefix}{nonce_text}', 'Nonce')

    expected_digest = _compute_digest(nonce, created_text, expected_password)

    out = is_string_equal(password_received, expected_digest)
    return out

# ################################################################################################################################

def _check_created(created_text:'str', skew_seconds:'int') -> 'None':
    """ Checks that a UsernameToken's wsu:Created puts it inside its validity window.
    """
    try:
        created = from_timestamp(created_text)
    except XMLException as e:
        raise SOAPSecurityException(e.args[0]) from e

    now = datetime.now(timezone.utc)
    skew = timedelta(seconds=skew_seconds)

    if created > now + skew:
        raise SOAPSecurityException('UsernameToken was created too far in the future')

    if created < now - timedelta(seconds=Created_TTL_Seconds) - skew:
        raise SOAPSecurityException('UsernameToken is too old')

# ################################################################################################################################

def verify_username_token(
    envelope:'any_',
    expected_username:'str',
    expected_password:'str',
    use_digest:'bool'=False,
    skew_seconds:'int'=Clock_Skew_Seconds,
    ) -> 'None':
    """ Verifies the wsse:UsernameToken of an incoming message against the expected credentials
    in the form the definition configured - which of the two forms is in use is the server's
    decision, not the caller's, or a client could always pick the weaker one.
    """
    security = get_security_header(envelope)
    token = security.find(qname(NS.WSSE, 'UsernameToken'))

    if token is None:
        raise SOAPSecurityException('Message has no UsernameToken')

    username_element = token.find(qname(NS.WSSE, 'Username'))

    if username_element is None:
        raise SOAPSecurityException('UsernameToken has no Username')

    password_element = token.find(qname(NS.WSSE, 'Password'))

    if password_element is None:
        raise SOAPSecurityException('UsernameToken has no Password')

    # The profile says an absent Type means clear text.
    password_type = password_element.get('Type')
    if password_type is None:
        password_type = _password_text

    if use_digest:
        expected_type = _password_digest
    else:
        expected_type = _password_text

    # Reading whichever type the message declares lets the client choose the scheme. A definition
    # configured for digest would then accept a clear-text password, and one configured for clear
    # text would accept a digest, which is a different secret from the one the operator set.
    if password_type != expected_type:
        raise SOAPSecurityException('UsernameToken password type is not the configured one')

    # An empty XML element carries None instead of text and this is external input,
    # so both credentials are normalized to empty strings for the comparisons below.
    username_received = element_text(username_element)
    password_received = element_text(password_element)

    if use_digest:
        password_matches = _verify_digest_password(token, password_received, expected_password, skew_seconds)
    else:
        password_matches = is_string_equal(password_received, expected_password)

    username_matches = is_string_equal(username_received, expected_username)

    if not username_matches:
        raise SOAPSecurityException('Username or password does not match')

    if not password_matches:
        raise SOAPSecurityException('Username or password does not match')

# ################################################################################################################################
# ################################################################################################################################
