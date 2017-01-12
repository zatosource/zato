# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import date as datetime_date
from decimal import Decimal, ROUND_CEILING, ROUND_DOWN
from unittest import TestCase

# dateutil
from dateutil.parser import parse as dateutil_parse

# Zato
from zato.server.service import fixed_width
from zato.server.service.reqresp.fixed_width import FixedWidth

Date = fixed_width.Date
FWDecimal = fixed_width.Decimal
Int = fixed_width.Int
String = fixed_width.String
Timestamp = fixed_width.Timestamp

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

    def test_parse_line_string(self):

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

    def test_parse_line_integer(self):

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

    def test_parse_line_decimal(self):

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

    def test_parse_line_decimal_rounding(self):

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

    def test_parse_line_decimal_rounding_with_context(self):

        class MyDecimal(FWDecimal):
            ctx_config = {
                'rounding': ROUND_CEILING
            }

        data = '1.112.22\n3.334.44'
        a = MyDecimal(4, 1, 'a')
        b = MyDecimal(4, 1, 'b')
        definition = (a, b)

        expected1 = [
            {'key':'a', 'value':Decimal('1.2')},
            {'key':'b', 'value':Decimal('2.3')},
        ]

        expected2 = [
            {'key':'a', 'value':Decimal('3.4')},
            {'key':'b', 'value':Decimal('4.5')},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_decimal_rounding_with_context_scale_zero(self):

        class MyDecimal(FWDecimal):
            ctx_config = {
                'rounding': ROUND_DOWN
            }

        data = '1.662.77\n3.884.99'
        a = MyDecimal(4, 0, 'a')
        b = MyDecimal(4, 0, 'b')
        definition = (a, b)

        expected1 = [
            {'key':'a', 'value':Decimal('1')},
            {'key':'b', 'value':Decimal('2')},
        ]

        expected2 = [
            {'key':'a', 'value':Decimal('3')},
            {'key':'b', 'value':Decimal('4')},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_timestamp_iso(self):

        data = '2015-06-23T21:22:23,123456   aaa\n2044-12-29T13:14:15,567890   bbb'
        ts = Timestamp(29, 'ts')
        str = String(3, 'str')
        definition = (ts, str)

        expected1 = [
            {'key':'ts', 'value':dateutil_parse('2015-06-23T21:22:23,123456')},
            {'key':'str', 'value':'aaa'},
        ]

        expected2 = [
            {'key':'ts', 'value':dateutil_parse('2044-12-29T13:14:15,567890')},
            {'key':'str', 'value':'bbb'},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_timestamp_custom_format(self):

        class MyTimestamp(Timestamp):
            parse_kwargs = {
                'date_formats': ['%b, %Y_%d//  --%I%p']
            }

        data = 'Jan, 1923_12//  --3pm aaa\nMar, 2732_11//  --7pm bbb'
        ts = MyTimestamp(22, 'ts')
        str = String(3, 'str')
        definition = (ts, str)

        expected1 = [
            {'key':'ts', 'value':dateutil_parse('1923-01-12T15:00')},
            {'key':'str', 'value':'aaa'},
        ]

        expected2 = [
            {'key':'ts', 'value':dateutil_parse('2732-03-11T19:00')},
            {'key':'str', 'value':'bbb'},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_date(self):

        data = '2015-06-23   aaa\n2044-12-29   bbb'
        date = Date(13, 'date')
        str = String(3, 'str')
        definition = (date, str)

        expected1 = [
            {'key':'date', 'value':datetime_date(2015, 6, 23)},
            {'key':'str', 'value':'aaa'},
        ]

        expected2 = [
            {'key':'date', 'value':datetime_date(2044, 12, 29)},
            {'key':'str', 'value':'bbb'},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_date_custom_format(self):

        class MyDate(Date):
            parse_kwargs = {
                'date_formats': ['%y%m---%d']
            }

        data = '9901---03aaa\n6612---23bbb'
        date = MyDate(9, 'date')
        str = String(3, 'str')
        definition = (date, str)

        expected1 = [
            {'key':'date', 'value':datetime_date(1999, 1, 3)},
            {'key':'str', 'value':'aaa'},
        ]

        expected2 = [
            {'key':'date', 'value':datetime_date(2066, 12, 23)},
            {'key':'str', 'value':'bbb'},
        ]

        fw = FixedWidth(data, definition)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################