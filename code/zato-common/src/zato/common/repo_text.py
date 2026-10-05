# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# This module has no Zato imports on purpose, the same file is also part of the Azure deploy program.

# stdlib
import re

# ################################################################################################################################
# ################################################################################################################################

strlist = list[str]

# ################################################################################################################################
# ################################################################################################################################

# The owner and name out of any address of a repository on GitHub.
_Repo_Label_Pattern = re.compile(r'github\.com[:/](?P<owner>[A-Za-z0-9_.-]+)/(?P<name>[A-Za-z0-9_.-]+?)(?:\.git)?/?$')

_Enmasse_Pattern = re.compile(r'(^|/)enmasse[^/]*\.ya?ml$')

# ################################################################################################################################
# ################################################################################################################################

def get_repo_label(url:'str') -> 'str':
    """ Returns owner/name for an address of a repository on GitHub, or the address itself if it is not one.
    """
    match = _Repo_Label_Pattern.search(url)

    if match:
        out = f'{match.group("owner")}/{match.group("name")}'
    else:
        out = url

    return out

# ################################################################################################################################

def count_text(count:'int', singular:'str', plural:'str'='') -> 'str':
    """ Returns the count with the noun in the right number, e.g. 1 branch, 2 branches.
    """
    if count == 1:
        noun = singular
    else:
        noun = plural or singular + 's'

    out = f'{count} {noun}'
    return out

# ################################################################################################################################

def summarize_changes(name_status:'str') -> 'str':
    """ Returns one line about what a pull changed, out of git's name-status listing, e.g.
    3 files changed - 2 services, 1 enmasse file.
    """
    services = 0
    enmasse  = 0
    other    = 0

    for line in name_status.splitlines():
        line = line.strip()

        if not line:
            continue

        # A line is the status, a tab and the path, a rename has the old and the new path.
        path = line.split('\t')[-1]

        if path.endswith('.py'):
            services += 1
        elif _Enmasse_Pattern.search(path):
            enmasse += 1
        else:
            other += 1

    total = services + enmasse + other

    if not total:
        return 'Nothing changed'

    parts:'strlist' = []

    if services:
        parts.append(count_text(services, 'service'))

    if enmasse:
        parts.append(count_text(enmasse, 'enmasse file'))

    if other:
        parts.append(count_text(other, 'other file'))

    out = f'{count_text(total, "file")} changed - {", ".join(parts)}'
    return out

# ################################################################################################################################
# ################################################################################################################################
