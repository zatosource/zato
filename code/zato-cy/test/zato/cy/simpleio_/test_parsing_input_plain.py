# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Service

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase, CySimpleIO, test_class_name

# ################################################################################################################################
# ################################################################################################################################

class InputPlainParsingTestCase(BaseTestCase):

    def test_convert_plain_into_required_optional(self):

        class SimpleIO:
            input = 'abc', 'zxc', 'ghj', '-rrr', '-eee'
            output = 'abc2', 'zxc2', 'ghj2', '-rrr2', '-eee2'

        sio = self.get_sio(SimpleIO, test_class_name)

        self.assertEquals(sio.definition._input_required.get_elem_names(), ['abc', 'ghj', 'zxc'])
        self.assertEquals(sio.definition._input_optional.get_elem_names(), ['eee', 'rrr'])

        self.assertEquals(sio.definition._output_required.get_elem_names(), ['abc2', 'ghj2', 'zxc2'])
        self.assertEquals(sio.definition._output_optional.get_elem_names(), ['eee2', 'rrr2'])

# ################################################################################################################################

    def test_elem_sharing_not_allowed_plain(self):

        class SimpleIO:
            input_required = 'abc', 'zxc', 'qwe', '-zxc', '-abc', '-rty'
            input_optional = 'zxc', 'abc', 'rty'

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Elements in input_required and input_optional cannot be shared, found:`['abc', 'zxc']` in `<my-test-class>`"
        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_elem_required_minus_is_insignificant(self):

        class MyService(Service):
            class SimpleIO:
                input_required = 'aaa', 'bbb', 'ccc', '-ddd', '-eee'
                output_required = 'qqq', 'www', '-eee', '-fff'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        self.assertEquals(MyService._sio.definition._input_required.get_elem_names(), ['-ddd', '-eee', 'aaa', 'bbb', 'ccc'])
        self.assertEquals(MyService._sio.definition._output_required.get_elem_names(), ['-eee', '-fff', 'qqq', 'www'])

# ################################################################################################################################
# ################################################################################################################################
