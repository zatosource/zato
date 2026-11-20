# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from live_windows.settings import Partners, Versions
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _pytest.python import Function
    from pytest import Item
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

itemlist = list['Item']

# ################################################################################################################################
# ################################################################################################################################

def _in_version_order(versions:'strlist') -> 'strlist':
    out:'strlist' = []

    for version in Versions.All:
        if version in versions:
            out.append(version)

    return out

# ################################################################################################################################

def item_versions(item:'Item') -> 'strlist':
    """ Returns the versions of the guests that a test runs against, in the order of all the versions.
    """
    versions:'strlist' = []

    # A test without a version parameter names its guests ..
    if marker := item.get_closest_marker('guests'):
        versions.extend(marker.args)

    # .. and a test with one runs against the guest of its version, and against the partner guest if it needs one.
    else:
        function:'Function' = cast_('Function', item)
        version:'str' = cast_('str', function.callspec.params['version'])
        versions.append(version)

        if item.get_closest_marker('partner_guest'):
            partner_version = Partners[version]
            versions.append(partner_version)

    out = _in_version_order(versions)
    return out

# ################################################################################################################################

def needed_versions(items:'itemlist') -> 'strlist':
    """ Returns the versions of the guests that any of the tests runs against.
    """
    versions:'strlist' = []

    for item in items:
        versions.extend(item_versions(item))

    out = _in_version_order(versions)
    return out

# ################################################################################################################################

def own_version(item:'Item') -> 'str':
    """ Returns the version that a test is about - the version it takes as its parameter, which its partner guest,
    if it needs one, only serves, or the first of the guests it names if it takes no version.
    """
    if marker := item.get_closest_marker('guests'):
        named_versions = list(marker.args)
        versions = _in_version_order(named_versions)
        out = versions[0]

    else:
        function:'Function' = cast_('Function', item)
        out = cast_('str', function.callspec.params['version'])

    return out

# ################################################################################################################################

def version_items(items:'itemlist', version:'str') -> 'itemlist':
    """ Returns the tests that are about the given version, in the order of their collection.
    """
    out:'itemlist' = []

    for item in items:
        if own_version(item) == version:
            out.append(item)

    return out

# ################################################################################################################################
# ################################################################################################################################
