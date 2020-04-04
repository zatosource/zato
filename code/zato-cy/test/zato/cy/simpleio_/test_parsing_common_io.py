# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from test.zato.cy.simpleio_ import BaseTestCase, test_class_name

# Python 2/3 compatibility
from past.builtins import str as past_str, unicode

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

        elem1 = repr(unicode('aaa'))
        elem2 = repr(unicode('bbb'))

        expected = "Cannot provide input_required if input is given, input:`qwerty`, " \
            "input_required:`({}, {})`, input_optional:`[]`".format(elem1, elem2)

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_input_and_input_optional_error(self):

        class SimpleIO:
            input = 'qwerty'
            input_optional = 'aaa', 'bbb'

        # Cannot have both input and input_required on input
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        elem1 = repr(unicode('aaa'))
        elem2 = repr(unicode('bbb'))

        expected = "Cannot provide input_optional if input is given, input:`qwerty`, " \
            "input_required:`[]`, input_optional:`({}, {})`".format(elem1, elem2)

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

        elem1 = repr(unicode('123'))
        elem2 = repr(unicode('456'))

        elem3 = repr(unicode('aaa'))
        elem4 = repr(unicode('bbb'))

        expected = "Cannot provide input_required/input_optional if input is given, input:`qwerty`, " \
            "input_required:`({}, {})`, input_optional:`({}, {})`".format(elem1, elem2, elem3, elem4)

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_output_and_output_required_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_required = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        elem1 = repr(unicode('aaa'))
        elem2 = repr(unicode('bbb'))

        expected = "Cannot provide output_required if output is given, output:`qwerty`, " \
            "output_required:`({}, {})`, output_optional:`[]`".format(elem1, elem2)

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_output_and_output_optional_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_optional = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        elem1 = repr(unicode('aaa'))
        elem2 = repr(unicode('bbb'))

        expected = "Cannot provide output_optional if output is given, output:`qwerty`, " \
            "output_required:`[]`, output_optional:`({}, {})`".format(elem1, elem2)

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

        elem1 = repr(unicode('123'))
        elem2 = repr(unicode('456'))

        elem3 = repr(unicode('aaa'))
        elem4 = repr(unicode('bbb'))

        expected = "Cannot provide output_required/output_optional if output is given, output:`qwerty`, " \
            "output_required:`({}, {})`, output_optional:`({}, {})`".format(elem1, elem2, elem3, elem4)

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_elem_sharing_not_allowed(self):

        class SimpleIO:
            input_required = 'abc', 'zxc', 'qwe'
            input_optional = 'zxc', 'abc', 'rty'

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        elem1 = repr(unicode('abc'))
        elem2 = repr(unicode('zxc'))

        expected = "Elements in input_required and input_optional cannot be shared, found:`[{}, {}]` in `<my-test-class>`".\
            format(elem1, elem2)

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def test_default_input_value(self):

        class SimpleIO:
            input_required = 'abc', 'zxc', 'qwe'
            input_optional = 'zxc', 'abc', 'rty'

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO, test_class_name)

        elem1 = repr(unicode('abc'))
        elem2 = repr(unicode('zxc'))

        expected = "Elements in input_required and input_optional cannot be shared, found:`[{}, {}]` in `<my-test-class>`".\
            format(elem1, elem2)

        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################
# ################################################################################################################################
