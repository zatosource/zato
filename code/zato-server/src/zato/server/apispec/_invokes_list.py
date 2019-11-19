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

class InvokesList(Service):
    name = '_test.invokes-list'
    invokes = ['_test.invokes-list2', '_test.invokes-list3']

# ################################################################################################################################

class InvokesList2(Service):
    name = '_test.invokes-list2'
    invokes = ['_test.invokes-list3']

# ################################################################################################################################

class InvokesList3(Service):
    name = '_test.invokes-list3'
    invokes = ['_test.invokes-list2']

# ################################################################################################################################
