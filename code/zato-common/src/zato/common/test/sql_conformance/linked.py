# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The registries of the repositories linked to this installation. A link declares its registry module under the key
# `registries` of its manifest, and the module defines each of the names that ModuleCtx lists, which the static scans
# of SQL conformance merge with the registries of the installation.

# stdlib
from importlib import import_module

# Zato
from zato_links.finder import get_links

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from types import ModuleType
    from zato.common.typing_ import any_, anylist

    ModuleType = ModuleType

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The key of a link with the name of its registry module
    Registries_Key = 'registries'

    # The names that a registry module defines
    Environment_Variables      = 'Environment_Variables'
    Direct_SQL_Purposes        = 'Direct_SQL_Purposes'
    Performance_Roots          = 'Performance_Roots'
    Memory_Database_Exemptions = 'Memory_Database_Exemptions'
    Mechanism_Functions        = 'Mechanism_Functions'
    Seed_Scratch_Tables        = 'Seed_Scratch_Tables'

# ################################################################################################################################
# ################################################################################################################################

def get_linked_registries() -> 'list[ModuleType]':
    """ Returns the registry module of each linked repository that declares one.
    """
    out:'list[ModuleType]' = []

    for link in get_links():
        if module_name := link.get(ModuleCtx.Registries_Key):
            module = import_module(module_name)
            out.append(module)

    return out

# ################################################################################################################################

def get_linked_entries(name:'str') -> 'anylist':
    """ Returns the entries of one registry, as all the linked repositories declare them together.
    """
    out:'anylist' = []

    for module in get_linked_registries():
        entries:'any_' = getattr(module, name)
        out.extend(entries)

    return out

# ################################################################################################################################
# ################################################################################################################################
