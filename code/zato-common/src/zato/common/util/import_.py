# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from importlib import import_module

# ################################################################################################################################
# ################################################################################################################################

def import_string(name):
    name = name.split('.')
    attr_name = name[-1]
    mod_name = '.'.join(name[:-1])
    mod = import_module(mod_name)
    return getattr(mod, attr_name)

# ################################################################################################################################
# ################################################################################################################################
