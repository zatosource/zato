# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger
from re import escape as re_escape
from urllib.parse import unquote

# Zato
from zato.common.api import HTTP_SOAP, MISC

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist
    any_ = any_
    anydict = anydict
    strlist = strlist

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

accept_any_http = HTTP_SOAP.ACCEPT.ANY
accept_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

# What a slash inside one path segment is spelled as, both on the way in and in a match target.
_encoded_slash = '%2F'

# Whether a path parameter matches a value spanning several path segments, for a channel
# whose configuration does not say either way.
Match_Slash_Default = True

# ################################################################################################################################

def resolve_match_slash(value:'any_') -> 'bool':
    """ Returns whether path parameters match across slashes for a channel whose configuration
    carries the given value, which a channel configured before the option existed does not carry.
    """
    if value is None:
        return Match_Slash_Default

    if value == '':
        return Match_Slash_Default

    out = bool(value)
    return out

# ################################################################################################################################

def to_internal_accept(http_accept:'str | None') -> 'str':
    """ Returns the form of an Accept header that channels are matched on, which both a channel's
    own configured value and an incoming header are turned into before the two ever meet.
    """
    if not http_accept:
        http_accept = accept_any_http

    out = http_accept.replace('*', accept_any_internal).replace('/', 'HTTP_SEP')

    return out

# ################################################################################################################################

def build_methods_allowed_re(http_methods_allowed:'strlist') -> 'str':
    """ Returns the pattern that stands in the method slot of a channel which names no method
    of its own, so that such a channel is reached with any of the methods a server allows.
    """
    alternatives = '|'.join(http_methods_allowed)

    # Non-capturing, because the runtime matcher takes a channel's path parameters
    # to be the only groups its pattern has.
    out = f'(?:{alternatives})'

    return out

# ################################################################################################################################

def _escape_url_path(url_path:'str') -> 'str':
    """ Escapes the literal parts of a channel's URL path, leaving its path parameters as they are,
    since the runtime matcher turns each of those into a named group of its own.
    """
    parts = []
    position = 0

    while True:

        start = url_path.find('{', position)

        # Nothing opens a parameter from here on, so what is left is literal
        if start == -1:
            break

        end = url_path.find('}', start)

        # A parameter that is never closed is literal as well
        if end == -1:
            break

        literal = url_path[position:start]
        parts.append(re_escape(literal))

        # The parameter's name goes in as it is, so that the matcher recognises it
        parts.append(url_path[start:end+1])

        position = end + 1

    parts.append(re_escape(url_path[position:]))

    out = ''.join(parts)
    return out

# ################################################################################################################################

def normalize_path_info(path_info:'str') -> 'str':
    """ Returns the form of the path a caller sent that channels are matched against - each segment
    percent-decoded, with empty and dot segments resolved.
    """
    segments = path_info.split('/')
    out_segments = []

    # Empty and dot segments are resolved before anything is decoded, so that decoding
    # cannot produce a segment of either kind afterwards ..
    for segment in segments:

        # An empty segment comes from the leading slash or from two slashes in a row
        if not segment:
            continue

        # A single dot stands for the path it sits in
        if segment == '.':
            continue

        # A double dot cancels the segment in front of it
        if segment == '..':
            if out_segments:
                _ = out_segments.pop()
            continue

        # .. each segment is decoded on its own and an encoded slash stays encoded,
        # .. because decoding it would add a separator the caller never sent.
        segment = unquote(segment)
        segment = segment.replace('/', _encoded_slash)

        out_segments.append(segment)

    joined = '/'.join(out_segments)
    out = f'/{joined}'

    # A path that ended with a slash keeps it, since a channel's own path may end with one too
    if path_info.endswith('/'):
        if out != '/':
            out = f'{out}/'

    return out

# ################################################################################################################################

def get_match_target(
    config:'anydict',
    sep:'str' = MISC.SEPARATOR,
    accept_any_http:'str' = accept_any_http,
    accept_any_internal:'str' = accept_any_internal,
    http_methods_allowed_re:'str | None' = None,
    ) -> 'str':

    http_method = config.get('method') or config.get('http_method')
    if not http_method:
        http_method = http_methods_allowed_re

    http_accept = to_internal_accept(config.get('http_accept'))

    # The Accept header and the URL path are matched literally, so whatever either of them
    # carries that a regular expression would read as syntax is escaped here. The internal
    # any/any marker is letters only, so it survives this and the matcher still recognises it.
    http_accept = re_escape(http_accept)

    url_path = _escape_url_path(config['url_path'])

    # Build the pattern - its first slot used to carry a SOAP action but channels
    # match by URL path alone now, the same way incoming requests do, and a channel's
    # SOAPAction is metadata that never participates in matching.
    pattern = f'{sep}{http_method}{sep}{http_accept}{sep}{url_path}'

    # .. and return it to our caller
    return pattern

# ################################################################################################################################
# ################################################################################################################################
