# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.simpleio import List

# ################################################################################################################################
# ################################################################################################################################

class AttachSIOTestCase(BaseSIOTestCase):
    def test_attach_sio(self):

        class MyService(Service):
            class SimpleIO:
                input = List('-aaa')

# ################################################################################################################################
# ################################################################################################################################
