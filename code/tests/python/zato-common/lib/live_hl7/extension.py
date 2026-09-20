# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from importlib import import_module

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from types import ModuleType

# ################################################################################################################################
# ################################################################################################################################

# More systems, groups and directories come from the package under Zato_Health_Root when it is set,
# exposing systems(), groups() and directories().
Extension_Root_Env = 'Zato_Health_Root'
Extension_Dir      = 'live'
Extension_Package  = 'health_live_hl7'

# ################################################################################################################################
# ################################################################################################################################

def _load_extension() -> 'ModuleType | None':
    root = os.environ.get(Extension_Root_Env)

    if not root:
        return None

    directory = os.path.join(root, Extension_Dir)
    package_directory = os.path.join(directory, Extension_Package)

    if not os.path.isdir(package_directory):
        return None

    if directory not in sys.path:
        sys.path.insert(0, directory)

    out = import_module(Extension_Package)
    return out

# ################################################################################################################################

extension = _load_extension()

# ################################################################################################################################

def extension_directory(name:'str', default:'str') -> 'str':
    """ The directory the extension has under this name, or the default when there is no extension or it has none.
    """
    if extension is None:
        return default

    directories = extension.directories()

    if name in directories:
        out = directories[name]
    else:
        out = default

    return out

# ################################################################################################################################
# ################################################################################################################################
