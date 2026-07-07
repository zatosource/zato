# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

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
