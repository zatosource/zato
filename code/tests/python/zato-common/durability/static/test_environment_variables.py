# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Zato
from zato.common.test.durability.linked import get_linked_entries, ModuleCtx as LinkedModuleCtx
from zato.common.test.durability.sources import get_source_files, ModuleCtx as SourcesModuleCtx

# Local
from registry import Environment_Variable_Keywords, Environment_Variables

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The name of an environment variable of Zato
    Name_Pattern = re.compile(r'\bZato_[A-Za-z0-9_]+')

    # The suffixes of the production sources in which an environment variable is read
    Suffixes = (SourcesModuleCtx.Python_Suffix, SourcesModuleCtx.Rust_Suffix)

# ################################################################################################################################
# ################################################################################################################################

def _has_keyword(name:'str') -> 'bool':
    lower_name = name.lower()

    for keyword in Environment_Variable_Keywords:
        if keyword.lower() in lower_name:
            return True

    return False

# ################################################################################################################################
# ################################################################################################################################

def test_environment_variables_listed() -> 'None':
    """ Each environment variable of production code whose name suggests that it changes when or how a write
    becomes durable is listed with what it controls, so that a new one fails until it is examined.
    """
    found:'set[str]' = set()

    for source in get_source_files():
        if source.is_production:
            if source.path.endswith(ModuleCtx.Suffixes):
                text = source.read()

                for match in ModuleCtx.Name_Pattern.finditer(text):
                    name = match.group(0)
                    if _has_keyword(name):
                        found.add(name)

    listed:'set[str]' = set()

    for name, _ in Environment_Variables:
        listed.add(name)

    for name, _ in get_linked_entries(LinkedModuleCtx.Environment_Variables):
        listed.add(name)

    unlisted = found - listed
    stale = listed - found

    assert not unlisted, f'Not listed: {sorted(unlisted)}'
    assert not stale, f'Listed but no longer used: {sorted(stale)}'

# ################################################################################################################################
# ################################################################################################################################
