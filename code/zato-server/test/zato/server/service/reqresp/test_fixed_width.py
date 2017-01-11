# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from decimal import Decimal
from unittest import TestCase

# Zato
from zato.server.service import fixed_width
from zato.server.service.reqresp.fixed_width import FixedWidth

FWDecimal = fixed_width.Decimal
Int = fixed_width.Int
String = fixed_width.String

# ################################################################################################################################

class TestParser(TestCase):

# ################################################################################################################################

    def compare_line(self, expected, actual):

        for expected_line in expected:
            expected_key = expected_line['key']
            expected_value = expected_line['value']
            actual_value = getattr(actual, expected_key)
            self.assertEquals(expected_value, actual_value)

# ################################################################################################################################

    def test_parse_line_string_only(self):

        data = 'abbcccdddd\nABBCCCDDDD'
        a = String(1, 'a')
        b = String(2, 'b')
        c = String(3, 'c')
        d = String(4, 'd')
        definition = (a, b, c, d)

        expected1 = [
            {'key':'a', 'value':'a'},
            {'key':'b', 'value':'bb'},
            {'key':'c', 'value':'ccc'},
            {'key':'d', 'value':'dddd'},
        ]

        expected2 = [
            {'key':'a', 'value':'A'},
            {'key':'b', 'value':'BB'},
            {'key':'c', 'value':'CCC'},
            {'key':'d', 'value':'DDDD'},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_integer_only(self):

        data = '1223334444\n5667778888'
        a = Int(1, 'a')
        b = Int(2, 'b')
        c = Int(3, 'c')
        d = Int(4, 'd')
        definition = (a, b, c, d)

        expected1 = [
            {'key':'a', 'value':1},
            {'key':'b', 'value':22},
            {'key':'c', 'value':333},
            {'key':'d', 'value':4444},
        ]

        expected2 = [
            {'key':'a', 'value':5},
            {'key':'b', 'value':66},
            {'key':'c', 'value':777},
            {'key':'d', 'value':8888},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_decimal_only(self):

        data = '1.122.22333.3334444.4444\n5.566.66777.7778888.8888'
        a = FWDecimal(3, 1, 'a')
        b = FWDecimal(5, 2, 'b')
        c = FWDecimal(7, 3, 'c')
        d = FWDecimal(9, 4, 'd')
        definition = (a, b, c, d)

        expected1 = [
            {'key':'a', 'value':Decimal('1.1')},
            {'key':'b', 'value':Decimal('22.22')},
            {'key':'c', 'value':Decimal('333.333')},
            {'key':'d', 'value':Decimal('4444.4444')},
        ]

        expected2 = [
            {'key':'a', 'value':Decimal('5.5')},
            {'key':'b', 'value':Decimal('66.66')},
            {'key':'c', 'value':Decimal('777.777')},
            {'key':'d', 'value':Decimal('8888.8888')},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_decimal_only_rounding(self):

        data = '1.112.22\n3.334.44'
        a = FWDecimal(4, 1, 'a')
        b = FWDecimal(4, 1, 'b')
        definition = (a, b)

        expected1 = [
            {'key':'a', 'value':Decimal('1.1')},
            {'key':'b', 'value':Decimal('2.2')},
        ]

        expected2 = [
            {'key':'a', 'value':Decimal('3.3')},
            {'key':'b', 'value':Decimal('4.4')},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################
