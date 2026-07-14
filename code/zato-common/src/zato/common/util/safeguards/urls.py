# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from re import compile as re_compile, IGNORECASE, Match

# Zato
from zato.common.typing_ import any_, strlist
from zato.common.util.safeguards.common import add_signal, Kind_Url, SafeguardConfig, SafeguardResult, Url_Marker, \
    Url_Mode_Neutralize, Url_Mode_Reject, Url_Mode_Remove
from zato.common.util.safeguards.walk import walk_strings

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
str_match = Match[str]

# ################################################################################################################################
# ################################################################################################################################

# The shape of a URL inside prose - a scheme, a host that starts with a name character,
# and everything up to whitespace or a closing delimiter.
Url_Pattern = re_compile(r'https?://[\w-]+[^\s<>"\')\]]*', IGNORECASE)

# Characters that end the host part of a URL.
Host_Delimiters = ('/', ':', '?', '#')

# ################################################################################################################################
# ################################################################################################################################

def _get_host(url:'str') -> 'str':
    """ Returns the lowercased host part of a URL.
    """

    # The scheme separator is always present because the URL pattern requires it ..
    _, _, host = url.partition('//')

    # .. and the host ends at the first delimiter that appears.
    for delimiter in Host_Delimiters:
        index = host.find(delimiter)

        if index != -1:
            host = host[:index]

    out = host.lower()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _is_host_allowed(host:'str', allow_list:'strlist') -> 'bool':
    """ Returns True if the host is one of the allowed suffixes or a subdomain of one.
    """
    for suffix in allow_list:

        # An exact match passes ..
        if host == suffix:
            out = True
            break

        # .. and so does any subdomain of an allowed suffix.
        if host.endswith('.' + suffix):
            out = True
            break

    # Anything else - including every host when the list is empty - does not pass.
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

def _remove_url(url:'str') -> 'str':
    """ Replaces a URL with the removal marker.
    """
    out = Url_Marker

    return out

# ################################################################################################################################
# ################################################################################################################################

def _neutralize_url(url:'str') -> 'str':
    """ Renders a URL harmless while keeping it recognizable - the scheme and the dots are broken up.
    """
    out = url.replace('http', 'hxxp', 1)
    out = out.replace('.', '[.]')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _keep_url(url:'str') -> 'str':
    """ Returns a URL unchanged - reject mode refuses the whole document, so individual URLs stay as they are.
    """
    out = url

    return out

# ################################################################################################################################
# ################################################################################################################################

# What to do with a flagged URL, by mode.
_url_transforms = {
    Url_Mode_Remove:     _remove_url,
    Url_Mode_Neutralize: _neutralize_url,
    Url_Mode_Reject:     _keep_url,
}

# ################################################################################################################################
# ################################################################################################################################

def apply_url_policy(value:'any_', result:'SafeguardResult', config:'SafeguardConfig') -> 'any_':
    """ Finds URLs in string values and removes, neutralizes or flags those whose host is outside the allow list.
    """

    # The allow list is matched case-insensitively, so it is lowercased once up front ..
    allow_list:'strlist' = []

    for entry in config.url_allow_list:
        allow_list.append(entry.lower())

    # .. and the mode picks what happens to every flagged URL.
    transform = _url_transforms[config.url_mode]

    def visit(text:'str', path:'str') -> 'str':

        def replace(match:'str_match') -> 'str':

            url = match.group(0)
            host = _get_host(url)

            # Allowed hosts pass untouched ..
            if _is_host_allowed(host, allow_list):
                return url

            # .. everything else is flagged and transformed.
            result.urls_flagged += 1
            add_signal(result.signals, Kind_Url, 1, path)

            out = transform(url)

            return out

        out = Url_Pattern.sub(replace, text)

        return out

    out = walk_strings(value, visit)

    return out

# ################################################################################################################################
# ################################################################################################################################
