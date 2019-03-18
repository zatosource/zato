# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

# Test support services below

# ################################################################################################################################

class Docstring(Service):
    """ Docstring Summary
    """
    name = '_test.docstring'

# ################################################################################################################################

class Docstring2(Service):
    """ Docstring2 Summary
    Docstring2 Description
    """
    name = '_test.docstring2'

# ################################################################################################################################

class Docstring3(Service):
    """ Docstring3 Summary

    Docstring3 Description

    Docstring3 Description2
    """
    name = '_test.docstring3'

# ################################################################################################################################
