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

class InvokesString(Service):
    name = '_test.invokes-string'
    invokes = '_test.invokes-string2'

# ################################################################################################################################

class InvokesString2(Service):
    name = '_test.invokes-string2'
    invokes = '_test.invokes-string3'

# ################################################################################################################################

class InvokesString3(Service):
    name = '_test.invokes-string3'
    invokes = '_test.invokes-string2'

# ################################################################################################################################
