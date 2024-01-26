# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.util.platform_ import is_non_windows

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

def parse_extra_into_list(data:'str') -> 'intlist':
    # type: (str) -> list
    return [int(elem.strip()) for elem in data.split(';') if elem]

# ################################################################################################################################

def path_string_to_list(base_dir:'str', data:'str') -> 'strlist':

    # A list of path strings to produce
    out = []

    # A list of path separators to try out
    path_sep_list = [',', ';']

    # This can be appended only if we are not on Windows where it would mean a drive name separator
    if is_non_windows:
        path_sep_list.append(':')

    # Try to find which path separator should be used, if any at all
    path_sep = None

    for elem in path_sep_list:
        if elem in data:
            path_sep = elem
            break

    # If there is no path separator, it means that there is no multi-element list to build,
    # in which case we turn the only string into the resulting list ..
    if not path_sep:
        path_data = [data]
    else:
        path_data = data.split(path_sep)

    # Remove whitespace for completeness
    path_data = [elem.strip() for elem in path_data]

    # Now, turn the list into absolute paths
    for path in path_data:
        if not os.path.isabs(path):
            path = os.path.join(base_dir, path)

        path = os.path.normpath(path)
        out.append(path)

    return out

# ################################################################################################################################

def path_string_list_to_list(base_dir:'str', data:'str | strlist') -> 'strlist':

    if isinstance(data, str):
        return path_string_to_list(base_dir, data)

    # A list of path strings to produce
    out = []

    for elem in data:
        result = path_string_to_list(base_dir, elem)
        out.extend(result)

    return out

# ################################################################################################################################
# ################################################################################################################################
