# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from hashlib import sha1
from os import urandom

# lxml
from lxml import etree

# Zato
from zato.common.crypto.api import is_string_equal
from zato.common.soap.common import NS, SOAPSecurityException
from zato.common.soap.envelope import get_security_header
from zato.common.util.xml_.core import qname, utc_timestamp
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

# How many random bytes go into a nonce.
_nonce_size_bytes = 16

# ################################################################################################################################
# ################################################################################################################################

def _compute_digest(nonce:'bytes', created:'str', password:'str') -> 'str':
    """ Computes the password digest from the UsernameToken profile -
    Base64(SHA-1(nonce + created + password)).
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
        nonce = urandom(_nonce_size_bytes)
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

def verify_username_token(envelope:'any_', expected_username:'str', expected_password:'str') -> 'None':
    """ Verifies the wsse:UsernameToken of an incoming message against the expected
    credentials, handling both the clear-text and the digest form.
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

    password_type = password_element.get('Type', _password_text)

    # An empty XML element carries None instead of text and this is external input,
    # so both credentials are normalized to empty strings for the comparisons below.
    username_received = username_element.text
    if username_received is None:
        username_received = ''

    password_received = password_element.text
    if password_received is None:
        password_received = ''

    # The digest form recomputes the digest from the message's own nonce and timestamp ..
    if password_type == _password_digest:
        nonce_element = token.find(qname(NS.WSSE, 'Nonce'))
        created_element = token.find(qname(NS.WSU, 'Created'))

        if nonce_element is None or created_element is None:
            raise SOAPSecurityException('Digest token has no Nonce or Created')

        nonce = decode_base64(nonce_element.text)
        expected_digest = _compute_digest(nonce, created_element.text, expected_password)

        password_matches = is_string_equal(password_received, expected_digest)

    # .. the clear-text form is a direct comparison.
    else:
        password_matches = is_string_equal(password_received, expected_password)

    username_matches = is_string_equal(username_received, expected_username)

    if not (username_matches and password_matches):
        raise SOAPSecurityException('Username or password does not match')

# ################################################################################################################################
# ################################################################################################################################
