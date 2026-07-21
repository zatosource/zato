# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NO_CONTENT

# Zato
from zato.common.http_ import HTTP_RESPONSES

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# Origins that are always allowed to make cross-origin requests to servers,
# e.g. the interactive tutorial pages on the documentation site
# and the same pages served locally while the documentation is being developed.
_allowed_origins = {
    'https://zato.io',
    'http://localhost',
    'http://127.0.0.1',
}

# Local origins are additionally allowed on any port - the trailing colon makes sure
# that only a port number can follow, so e.g. http://localhost.example.com will not match.
_allowed_origin_prefixes = (
    'http://localhost:',
    'http://127.0.0.1:',
)

# ################################################################################################################################

_header_allow_origin  = 'Access-Control-Allow-Origin'
_header_allow_methods = 'Access-Control-Allow-Methods'
_header_allow_headers = 'Access-Control-Allow-Headers'
_header_max_age       = 'Access-Control-Max-Age'

_allow_methods = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
_allow_headers = 'X-API-Key, Authorization, Content-Type'

# How long a browser may cache the result of a preflight request, in seconds.
_max_age = '86400'

# ################################################################################################################################

_status_no_content = '{} {}'.format(NO_CONTENT, HTTP_RESPONSES[NO_CONTENT])

# ################################################################################################################################
# ################################################################################################################################

def is_allowed_origin(origin:'str') -> 'bool':
    """ Returns True if the given Origin header value is one that servers accept for cross-origin requests.
    """

    # Exact matches cover the documentation site and local origins on the default port ..
    if origin in _allowed_origins:
        return True

    # .. otherwise, local origins are allowed on any port.
    for prefix in _allowed_origin_prefixes:
        if origin.startswith(prefix):
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def add_cors_response_headers(origin:'str', wsgi_environ:'stranydict') -> 'None':
    """ Adds the header that lets a browser expose our response to a page from an allowed origin.
    Note that the header may carry one origin only, which is why the matched origin is echoed back.
    """
    wsgi_environ['zato.http.response.headers'][_header_allow_origin] = origin

# ################################################################################################################################

def handle_preflight_request(origin:'str', wsgi_environ:'stranydict') -> 'str':
    """ Answers a CORS preflight request. This runs before authentication because preflights never carry credentials,
    so letting them reach a channel would end in an authentication error and the browser would block the actual request.
    """

    # Tell the browser what the actual request may look like ..
    headers = wsgi_environ['zato.http.response.headers']
    headers[_header_allow_origin]  = origin
    headers[_header_allow_methods] = _allow_methods
    headers[_header_allow_headers] = _allow_headers
    headers[_header_max_age]       = _max_age

    # .. a preflight response carries no body, which its status also indicates.
    wsgi_environ['zato.http.response.status'] = _status_no_content

    out = ''
    return out

# ################################################################################################################################
# ################################################################################################################################
