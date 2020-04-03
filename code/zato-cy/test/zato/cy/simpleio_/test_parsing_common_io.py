# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from test.zato.cy.simpleio_ import BaseTestCase, test_class_name

# ################################################################################################################################
# ################################################################################################################################

class InputOutputParsingTestCase(BaseTestCase):

    def test_no_input_output(self):

        class SimpleIO:
            pass

        # Providing such a bare declaration should not raise an exception
        self.get_sio(SimpleIO, test_class_name)

# ################################################################################################################################

    def test_input_and_input_required_error(self):

        class SimpleIO:
            input = 'qwerty'
            input_required = 'aaa', 'bbb'

        # Cannot have both input and input_required on input
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Cannot provide input_required if input is given, input:`qwerty`, " \
            "input_required:`('aaa', 'bbb')`, input_optional:`[]`"

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_input_and_input_optional_error(self):

        class SimpleIO:
            input = 'qwerty'
            input_optional = 'aaa', 'bbb'

        # Cannot have both input and input_required on input
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Cannot provide input_optional if input is given, input:`qwerty`, " \
            "input_required:`[]`, input_optional:`('aaa', 'bbb')`"

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_input_and_input_required_optional_error(self):

        class SimpleIO:
            input = 'qwerty'
            input_required = '123', '456'
            input_optional = 'aaa', 'bbb'

        # Cannot have both input and input_required on input
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Cannot provide input_required/input_optional if input is given, input:`qwerty`, " \
            "input_required:`('123', '456')`, input_optional:`('aaa', 'bbb')`"

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_output_and_output_required_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_required = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Cannot provide output_required if output is given, output:`qwerty`, " \
            "output_required:`('aaa', 'bbb')`, output_optional:`[]`"

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_output_and_output_optional_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_optional = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Cannot provide output_optional if output is given, output:`qwerty`, " \
            "output_required:`[]`, output_optional:`('aaa', 'bbb')`"

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_output_and_output_required_optional_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_required = '123', '456'
            output_optional = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Cannot provide output_required/output_optional if output is given, output:`qwerty`, " \
            "output_required:`('123', '456')`, output_optional:`('aaa', 'bbb')`"

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def xtest_elem_sharing_not_allowed(self):

        class SimpleIO:
            input_required = 'abc', 'zxc', 'qwe'
            input_optional = 'zxc', 'abc', 'rty'

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Elements in input_required and input_optional cannot be shared, found:`[u'abc', u'zxc']` in `<my-test-class>`"
        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_default_input_value(self):

        class SimpleIO:
            input_required = 'abc', 'zxc', 'qwe'
            input_optional = 'zxc', 'abc', 'rty'

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        expected = "Elements in input_required and input_optional cannot be shared, found:`[b'abc', b'zxc']` in `<my-test-class>`"
        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################
# ################################################################################################################################
