# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# Zato
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA

# ################################################################################################################################
# ################################################################################################################################

def get_converter_dir() -> 'str':
    """ Returns the directory the converter is installed in - the environment variable when it is set,
    otherwise a directory next to the Python interpreter.
    """
    out = os.environ.get(_ccda.Env_Dir)

    if not out:
        bin_dir = os.path.dirname(sys.executable)
        out = os.path.join(bin_dir, _ccda.Default_Dir_Name)

    return out

# ################################################################################################################################

def get_binary_path() -> 'str':
    """ Returns the path to the converter's binary.
    """
    out = os.path.join(get_converter_dir(), _ccda.Binary_Name)
    return out

# ################################################################################################################################

def get_templates_dir() -> 'str':
    """ Returns the directory of the C-CDA templates the converter reads.
    """
    out = os.path.join(get_converter_dir(), _ccda.Templates_Dir_Name, _ccda.Templates_Set_Name)
    return out

# ################################################################################################################################

def is_converter_installed() -> 'bool':
    """ Tells whether both the binary and its templates are in place.
    """
    has_binary    = os.path.isfile(get_binary_path())
    has_templates = os.path.isdir(get_templates_dir())

    out = has_binary and has_templates
    return out

# ################################################################################################################################
# ################################################################################################################################
