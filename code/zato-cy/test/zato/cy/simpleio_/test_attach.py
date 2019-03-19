# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

class AttachSIOTestCase(BaseTestCase):
    def test_attach_sio(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', 'ccc', '-ddd', '-eee'
                output = 'qqq', 'www', '-eee', '-fff'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        self.assertEquals(MyService._sio.definition._input_required.get_elem_names(), ['aaa', 'bbb', 'ccc'])
        self.assertEquals(MyService._sio.definition._input_optional.get_elem_names(), ['ddd', 'eee'])

        self.assertEquals(MyService._sio.definition._output_required.get_elem_names(), ['qqq', 'www'])
        self.assertEquals(MyService._sio.definition._output_optional.get_elem_names(), ['eee', 'fff'])

# ################################################################################################################################
# ################################################################################################################################
