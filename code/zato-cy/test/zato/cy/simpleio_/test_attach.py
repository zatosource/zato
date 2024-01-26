# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

class AttachSIOTestCase(BaseSIOTestCase):
    def test_attach_sio(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', 'ccc', '-ddd', '-eee'
                output = 'qqq', 'www', '-eee', '-fff'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        self.assertEqual(MyService._sio.definition._input_required.get_elem_names(), ['aaa', 'bbb', 'ccc'])
        self.assertEqual(MyService._sio.definition._input_optional.get_elem_names(), ['ddd', 'eee'])

        self.assertEqual(MyService._sio.definition._output_required.get_elem_names(), ['qqq', 'www'])
        self.assertEqual(MyService._sio.definition._output_optional.get_elem_names(), ['eee', 'fff'])

        self.assertTrue(MyService._sio.definition.has_input_required)
        self.assertTrue(MyService._sio.definition.has_input_optional)

        self.assertTrue(MyService._sio.definition.has_output_required)
        self.assertTrue(MyService._sio.definition.has_output_optional)

# ################################################################################################################################
# ################################################################################################################################
