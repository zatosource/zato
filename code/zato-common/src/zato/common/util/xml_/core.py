# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def qname(namespace:'str', tag:'str') -> 'str':
    """ Returns the fully-qualified lxml tag name for a namespace and local name.
    """
    out = f'{{{namespace}}}{tag}'
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
