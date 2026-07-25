# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from functools import lru_cache
from uuid import UUID

# lxml
from lxml import etree

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# How much randomness goes into the identifiers that signatures, timestamps and encrypted
# parts reference each other by - 128 bits, i.e. 32 hexadecimal characters.
Id_Size_Bits = 128

# A UUID is 128 bits wide, of which six are the version and variant bits that RFC 4122 fixes,
# so a random version 4 UUID carries 122 bits of randomness.
_uuid_size_bits = 128

# How many qualified names are kept. The namespaces and local names come from the specifications
# this implementation speaks, not from message content, so the real number of distinct pairs is in
# the low hundreds - this is a ceiling that also bounds the cache should a caller ever pass a name
# taken from a message.
QName_Cache_Size = 4096

# The one hardened parser every XML parse in the SOAP family goes through. Each setting closes
# a specific attack: resolve_entities stops XXE and billion-laughs expansion, no_network stops
# the parser reaching out to fetch anything a document names, load_dtd stops an inline or
# external DTD from being processed at all, and huge_tree keeps libxml2's depth and size guards
# in place. Callers must not build their own parser - a parse that skips these settings is a
# file-read and denial-of-service hole on any path that sees untrusted input.
#
# An lxml parser instance is not thread-safe. Zato runs one OS thread per worker and everything
# above it is greenlets, which are cooperatively scheduled and therefore never re-enter a parse,
# so a single shared instance is safe here. It must never be handed to a real threadpool.
xml_parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False)

# ################################################################################################################################
# ################################################################################################################################

@lru_cache(maxsize=QName_Cache_Size)
def qname(namespace:'str', tag:'str') -> 'str':
    """ Returns the fully-qualified lxml tag name for a namespace and local name.

    The result is cached because this is called several times per element on every message and the
    arguments are a small fixed set of namespaces and local names drawn from the specifications this
    implementation speaks - so the cache holds every combination that will ever be asked for after
    the first few messages, and each later call is a dict lookup instead of building a string.
    """
    out = f'{{{namespace}}}{tag}'
    return out

# ################################################################################################################################

def new_id(prefix:'str') -> 'str':
    """ Returns a fresh identifier for an element that another element references by id -
    the prefix says what kind of element it is, e.g. SIG- for a signature.
    """
    out = f'{prefix}{CryptoManager.generate_hex_string(Id_Size_Bits)}'
    return out

# ################################################################################################################################

def new_uuid_urn() -> 'str':
    """ Returns a fresh urn:uuid identifier - the form WS-Addressing and ebMS recommend
    for message ids. The randomness comes from CryptoManager, and UUID fixes the version
    and variant bits so the result is a well-formed RFC 4122 version 4 UUID that a strict
    peer will accept.
    """
    random_hex = CryptoManager.generate_hex_string(_uuid_size_bits)

    out = f'urn:uuid:{UUID(hex=random_hex, version=4)}'
    return out

# ################################################################################################################################

def to_timestamp(when:'datetime') -> 'str':
    """ Returns a datetime in the xsd:dateTime format that SOAP-family messages use.
    """
    out = when.strftime('%Y-%m-%dT%H:%M:%S.') + f'{when.microsecond // 1000:03d}Z'
    return out

# ################################################################################################################################

def utc_timestamp() -> 'str':
    """ Returns the current UTC time in the xsd:dateTime format that SOAP-family messages use.
    """
    out = to_timestamp(datetime.now(timezone.utc))
    return out

# ################################################################################################################################

def from_timestamp(text:'str') -> 'datetime':
    """ Parses an xsd:dateTime out of a message and returns it as an aware datetime in UTC.
    The value comes from the wire, so anything that is not a timestamp raises XMLException
    rather than one of the several exception types the parsing itself can produce.
    """
    try:
        parsed = datetime.fromisoformat(text.strip())
    except ValueError:
        raise XMLException(f'Not a timestamp -> `{text}`')

    # xsd:dateTime allows the timezone to be omitted, in which case the specification leaves the
    # zone undetermined. Everything in this family writes UTC, so an absent zone is read as UTC -
    # the alternative is to reject the value, which would break peers that omit it.
    if parsed.tzinfo is None:
        out = parsed.replace(tzinfo=timezone.utc)
    else:
        out = parsed.astimezone(timezone.utc)

    return out

# ################################################################################################################################

def element_text(element:'any_') -> 'str':
    """ Returns the text of an element - an empty element genuinely carries None.
    """
    out = element.text
    if out is None:
        out = ''

    return out

# ################################################################################################################################

def element_attribute(element:'any_', name:'str') -> 'str':
    """ Returns the value of an element's attribute - a missing attribute genuinely yields None.
    """
    out = element.get(name)
    if out is None:
        out = ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class XMLException(Exception):
    """ Raised when generic XML processing fails - e.g. a message carries
    a value of a type that has no XML lexical form.
    """

# ################################################################################################################################
# ################################################################################################################################

class XMLSecurityException(Exception):
    """ Raised when a shared XML security primitive fails - signature verification,
    trust validation, token parsing or key recovery.
    """

# ################################################################################################################################
# ################################################################################################################################

class XMLSecurityUnsupportedAlgorithm(XMLSecurityException):
    """ Raised when a message uses an algorithm this implementation does not support -
    callers may want to report this differently from a plain verification failure.
    """

# ################################################################################################################################
# ################################################################################################################################
