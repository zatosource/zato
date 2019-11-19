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

class Name(Service):
    name = '_test.name'

# ################################################################################################################################

class Name2(Service):
    name = '_test.name2'

# ################################################################################################################################

class Name3(Service):
    name = '_test.name3'

# ################################################################################################################################
