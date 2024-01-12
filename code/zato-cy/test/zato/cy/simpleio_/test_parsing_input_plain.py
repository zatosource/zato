# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.test import BaseSIOTestCase, test_class_name
from zato.server.service import Service

# Zato - Cython
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

class InputPlainParsingTestCase(BaseSIOTestCase):

    def test_convert_plain_into_required_optional(self):

        class SimpleIO:
            input = 'abc', 'zxc', 'ghj', '-rrr', '-eee'
            output = 'abc2', 'zxc2', 'ghj2', '-rrr2', '-eee2'

        sio = self.get_sio(SimpleIO, test_class_name)

        self.assertEqual(sio.definition._input_required.get_elem_names(), ['abc', 'ghj', 'zxc'])
        self.assertEqual(sio.definition._input_optional.get_elem_names(), ['eee', 'rrr'])

        self.assertEqual(sio.definition._output_required.get_elem_names(), ['abc2', 'ghj2', 'zxc2'])
        self.assertEqual(sio.definition._output_optional.get_elem_names(), ['eee2', 'rrr2'])

# ################################################################################################################################

    def test_elem_required_minus_is_insignificant(self):

        class MyService(Service):
            class SimpleIO:
                input_required = 'aaa', 'bbb', 'ccc', '-ddd', '-eee'
                output_required = 'qqq', 'www', '-eee', '-fff'

        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        self.assertEqual(MyService._sio.definition._input_required.get_elem_names(), ['-ddd', '-eee', 'aaa', 'bbb', 'ccc'])
        self.assertEqual(MyService._sio.definition._output_required.get_elem_names(), ['-eee', '-fff', 'qqq', 'www'])

# ################################################################################################################################
# ################################################################################################################################
