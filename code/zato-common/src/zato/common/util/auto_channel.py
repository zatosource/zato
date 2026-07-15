# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass, field
from re import compile as re_compile

# Zato
from zato.common.util.eval_ import as_bool

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The global on/off variable - the whole feature is enabled unless this one turns it off,
# and with no include patterns set the feature never creates anything anyway.
Env_Enabled = 'Zato_Auto_REST_Channel_Enabled'

# The URL prefix all auto-created channels share
Env_Prefix = 'Zato_Auto_REST_Channel_Prefix'

# Each family is open-ended - the base name plus any number of suffixed variables,
# e.g. Zato_Auto_REST_Channel_Include, Zato_Auto_REST_Channel_Include_01, Zato_Auto_REST_Channel_Include_ABC.
Family_Include = 'Zato_Auto_REST_Channel_Include'
Family_Exclude = 'Zato_Auto_REST_Channel_Exclude'
Family_Active = 'Zato_Auto_REST_Channel_Active'

# The default URL prefix for auto-created channels
Default_Prefix = '/api/'

# Patterns inside one variable are separated by a comma or a semicolon, with optional spaces around each separator
_pattern_separator = re_compile('[,;]')

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class AutoChannelConfig:
    """ Everything the auto-channel feature reads from the environment, collected in one place.
    """
    is_enabled: 'bool' = True
    url_prefix: 'str' = Default_Prefix
    include: 'strlist' = field(default_factory=list)
    exclude: 'strlist' = field(default_factory=list)
    active: 'strlist' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

def collect_family_patterns(family:'str', environ:'any_') -> 'strlist':
    """ Collects the patterns from all the variables belonging to one family - the base name and any
    suffixed variants - with the variables sorted lexicographically by name and each value split
    on commas or semicolons with optional surrounding spaces.
    """
    out = []

    for name in sorted(environ):
        if not name.startswith(family):
            continue

        value = environ[name]

        for pattern in _pattern_separator.split(value):
            pattern = pattern.strip()
            if pattern:
                out.append(pattern)

    return out

# ################################################################################################################################

def matches_pattern(service_name:'str', pattern:'str') -> 'bool':
    """ Matches a dotted service name against a dotted pattern where each {placeholder} matches
    exactly one dotted segment - never more, never less - and every other segment must be equal literally.
    """
    name_parts = service_name.split('.')
    pattern_parts = pattern.split('.')

    # A placeholder matches one segment, so the segment counts always have to be equal
    if len(name_parts) != len(pattern_parts):
        return False

    for name_part, pattern_part in zip(name_parts, pattern_parts):

        # A whole-segment placeholder matches whatever this one segment is ..
        if pattern_part.startswith('{') and pattern_part.endswith('}'):
            continue

        # .. and everything else is a literal comparison, with no glob stars anywhere.
        if name_part != pattern_part:
            return False

    return True

# ################################################################################################################################

def matches_any(service_name:'str', patterns:'strlist') -> 'bool':
    """ Matches a dotted service name against a list of patterns, True if at least one of them matches.
    """
    for pattern in patterns:
        if matches_pattern(service_name, pattern):
            return True

    return False

# ################################################################################################################################

def get_auto_channel_config(environ:'any_'=None) -> 'AutoChannelConfig':
    """ Reads the full auto-channel configuration out of the environment.
    """
    if environ is None:
        environ = os.environ

    out = AutoChannelConfig()

    # The feature is on unless the global variable turns it off
    if Env_Enabled in environ:
        out.is_enabled = as_bool(environ[Env_Enabled])

    # The prefix always begins and ends with a slash, no matter how it was spelled
    if Env_Prefix in environ:
        prefix = environ[Env_Prefix].strip()

        if not prefix.startswith('/'):
            prefix = '/' + prefix

        if not prefix.endswith('/'):
            prefix = prefix + '/'

        out.url_prefix = prefix

    out.include = collect_family_patterns(Family_Include, environ)
    out.exclude = collect_family_patterns(Family_Exclude, environ)
    out.active = collect_family_patterns(Family_Active, environ)

    return out

# ################################################################################################################################

def should_create_channel(service_name:'str', config:'AutoChannelConfig') -> 'bool':
    """ Decides whether a service gets an auto-created channel - the feature has to be on,
    the name has to match an include pattern and no exclude pattern may match it.
    """
    if not config.is_enabled:
        return False

    if not matches_any(service_name, config.include):
        return False

    if matches_any(service_name, config.exclude):
        return False

    return True

# ################################################################################################################################

def is_channel_active(service_name:'str', config:'AutoChannelConfig') -> 'bool':
    """ Decides whether a service's auto-created channel starts as active - only a match against
    the active patterns makes it so, everything else is created inactive (and an inactive channel
    does not respond at its URL at all).
    """
    return matches_any(service_name, config.active)

# ################################################################################################################################

def get_auto_channel_url_path(service_name:'str', config:'AutoChannelConfig') -> 'str':
    """ Returns the URL path of a service's auto-created channel - the prefix plus the service name
    with dots turned into slashes.
    """
    return config.url_prefix + service_name.replace('.', '/')

# ################################################################################################################################
# ################################################################################################################################
