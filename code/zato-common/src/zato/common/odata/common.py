# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strnone

# ################################################################################################################################
# ################################################################################################################################

class ODataVersion:
    """ The two OData protocol versions in use.
    """
    V2 = '2.0'
    V4 = '4.0'

# ################################################################################################################################
# ################################################################################################################################

class AuthType:
    """ The authentication schemes an OData connection may use.
    """
    No_Auth = 'no-auth'
    Basic   = 'basic'
    Bearer  = 'bearer'
    OAuth2  = 'oauth2'

# ################################################################################################################################
# ################################################################################################################################

# The Content-Type of every JSON request either version sends.
Content_Type_JSON = 'application/json'

# The Accept header each version asks for - V4 requests minimal metadata the way
# OASIS OData 4.01 Part 1 section 13 prescribes for interoperable clients.
Accept_Header = {
    ODataVersion.V2: 'application/json',
    ODataVersion.V4: 'application/json;odata.metadata=minimal',
}

# ################################################################################################################################
# ################################################################################################################################

class ODataException(Exception):
    """ Base class for all OData-related exceptions.
    """

# ################################################################################################################################
# ################################################################################################################################

class ODataSyntaxError(ODataException):
    """ Raised when a response cannot be parsed as the JSON payload it claims to be.
    """

# ################################################################################################################################
# ################################################################################################################################

class ODataError(ODataException):
    """ An OData error of either version, surfaced as one exception type - the HTTP status,
    the error code and message from the payload, plus any per-item details a V4 server includes.
    """
    def __init__(self, status_code:'int', code:'str', message:'str', details:'anylist') -> 'None':
        super().__init__(f'{status_code} {code} {message}')
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details

# ################################################################################################################################
# ################################################################################################################################

def parse_error(status_code:'int', data:'anydict') -> 'ODataError':
    """ Builds an ODataError out of the JSON error payload of either version. V4 carries
    {'error': {'code', 'message', 'details'}} with a string message, V2 nests the message
    as {'lang', 'value'}, and both shapes surface as the same exception.
    """
    error = data['error']

    code = error.get('code') or ''
    message = error.get('message') or ''

    # V2 wraps the human-readable text in a language-tagged object.
    if isinstance(message, dict):
        message = message['value']

    details = error.get('details') or []

    out = ODataError(status_code, code, message, details)
    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_items(data:'anydict', odata_version:'str') -> 'anylist':
    """ Returns the list of entities from a feed response of either version - V4 keeps them
    under 'value', V2 under 'd' which is either the list itself or wraps it in 'results'.
    """
    if odata_version == ODataVersion.V2:
        payload = data['d']

        # The verbose V2 format wraps the list, older servers return it directly.
        if isinstance(payload, dict):
            out = payload['results']
        else:
            out = payload

    else:
        out = data['value']

    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_entity(data:'anydict', odata_version:'str') -> 'anydict':
    """ Returns a single entity from a response of either version - V4 entities arrive
    at the top level, V2 wraps them in 'd'.
    """
    if odata_version == ODataVersion.V2:
        out = data['d']
    else:
        out = data

    return out

# ################################################################################################################################
# ################################################################################################################################

def extract_next_link(data:'anydict', odata_version:'str') -> 'strnone':
    """ Returns the next-page link of a feed response, or None when this was the last page -
    V4 announces it as '@odata.nextLink', V2 as '__next' inside 'd'.
    """
    if odata_version == ODataVersion.V2:
        payload = data['d']

        # Only the verbose V2 format can carry a next link at all.
        if isinstance(payload, dict):
            out = payload.get('__next')
        else:
            out = None

    else:
        out = data.get('@odata.nextLink')

    return out

# ################################################################################################################################
# ################################################################################################################################
