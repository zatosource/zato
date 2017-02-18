# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import date as datetime_date, datetime as datetime_datetime, time as datetime_time
from decimal import Decimal, ROUND_CEILING, ROUND_DOWN
from unittest import TestCase

# Bunch
from bunch import Bunch

# dateutil
from dateutil.parser import parse as dateutil_parse

# Zato
from zato.common import PADDING
from zato.server.service import fixed_width
from zato.server.service.reqresp.fixed_width import FixedWidth

Date = fixed_width.Date
FWDecimal = fixed_width.Decimal
Int = fixed_width.Int
String = fixed_width.String
Time = fixed_width.Time
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

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_string_strip(self):

        data = ' a   bb    cccdddd   \n A   BB    CCCDDDD   '
        a = String(3, 'a')
        b = String(6, 'b')
        c = String(5, 'c')
        d = String(7, 'd')
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_integer_strip(self):

        data = ' 1 22  333   4444\n 5 66  777   8888'
        a = Int(3, 'a')
        b = Int(4, 'b')
        c = Int(3, 'c')
        d = Int(7, 'd')
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_decimal_strip(self):

        data = ' 1.1 22.22    333.3334444.4444     \n 5.5 66.66    777.7778888.8888     '
        a = FWDecimal(5, 1, 'a')
        b = FWDecimal(9, 2, 'b')
        c = FWDecimal(7, 3, 'c')
        d = FWDecimal(14, 4, 'd')
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

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_decimal_strip_custom(self):

        data = '0001.10000022.22333.33304444.4444\n0005.50000066.66777.77708888.8888'
        a = FWDecimal(6, 1, 'a')
        b = FWDecimal(10, 2, 'b')
        c = FWDecimal(7, 3, 'c')
        d = FWDecimal(10, 4, 'd')
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

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_decimal_has_dec_sep_false(self):

        class MyDecimal(FWDecimal):
            has_dec_sep = False

        data = '11222233333344444444\n55666677777788888888'
        a = MyDecimal(2, 1, 'a')
        b = MyDecimal(4, 2, 'b')
        c = MyDecimal(6, 3, 'c')
        d = MyDecimal(8, 4, 'd')
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
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

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_time(self):

        data = '23:21:12   aaa\n19:22:44   bbb'
        time = Time(11, 'time')
        str = String(3, 'str')
        definition = (time, str)

        expected1 = [
            {'key':'time', 'value':datetime_time(23, 21, 12)},
            {'key':'str', 'value':'aaa'},
        ]

        expected2 = [
            {'key':'time', 'value':datetime_time(19, 22, 44)},
            {'key':'str', 'value':'bbb'},
        ]

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

    def test_parse_line_time_custom_format(self):

        data = '02_21_12   aaa\n07_22_44   bbb'
        time = Time(11, 'time', parse_kwargs={'date_formats': ['%H_%M_%S']})
        str = String(3, 'str')
        definition = (time, str)

        expected1 = [
            {'key':'time', 'value':datetime_time(2, 21, 12)},
            {'key':'str', 'value':'aaa'},
        ]

        expected2 = [
            {'key':'time', 'value':datetime_time(7, 22, 44)},
            {'key':'str', 'value':'bbb'},
        ]

        fw = FixedWidth(definition, data)
        elems = list(fw)

        actual1 = elems[0]
        actual2 = elems[1]

        self.compare_line(expected1, actual1)
        self.compare_line(expected2, actual2)

# ################################################################################################################################

class TestSerialize(TestCase):

# ################################################################################################################################

    def test_serialize_line_string(self):

        a = String(1, 'a')
        b = String(2, 'b')
        c = String(3, 'c')
        d = String(4, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 'a'
        response.b = 'bb'
        response.c = 'ccc'
        response.d = 'dddd'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, 'abbcccdddd')

# ################################################################################################################################

    def test_serialize_multiline_string(self):

        a = String(1, 'a')
        b = String(2, 'b')
        c = String(3, 'c')
        d = String(4, 'd')
        definition = (a, b, c, d)

        line1 = Bunch()
        line1.a = 'a'
        line1.b = 'bb'
        line1.c = 'ccc'
        line1.d = 'dddd'

        line2 = Bunch()
        line2.a = 'A'
        line2.b = 'BB'
        line2.c = 'CCC'
        line2.d = 'DDDD'

        response = [line1, line2]

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, 'abbcccdddd\nABBCCCDDDD')

# ################################################################################################################################

    def test_serialize_line_string_padding_right(self):

        a = String(1, 'a')
        b = String(2, 'b')
        c = String(3, 'c')
        d = String(4, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 'a'
        response.b = 'b'
        response.c = 'cc'
        response.d = 'd'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, 'ab cc d   ')

# ################################################################################################################################

    def test_serialize_line_string_padding_left(self):

        class MyString(String):
            padding = PADDING.LEFT

        a = MyString(1, 'a')
        b = MyString(2, 'b')
        c = MyString(3, 'c')
        d = MyString(4, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 'a'
        response.b = 'b'
        response.c = 'cc'
        response.d = 'd'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, 'a b cc   d')

# ################################################################################################################################

    def test_serialize_line_string_padding_right_fill_char(self):

        a = String(1, 'a')
        b = String(2, 'b')
        c = String(3, 'c', fill_char='#')
        d = String(4, 'd', fill_char='^')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 'a'
        response.b = 'b'
        response.c = 'cc'
        response.d = 'd'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, 'ab cc#d^^^')

# ################################################################################################################################

    def test_serialize_line_string_padding_left_fill_char(self):

        class MyString(String):
            padding = PADDING.LEFT
            fill_char = 'Z'

        a = MyString(1, 'a')
        b = MyString(2, 'b')
        c = MyString(3, 'c', fill_char='*')
        d = MyString(4, 'd', fill_char='7')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 'a'
        response.b = 'b'
        response.c = 'cc'
        response.d = 'd'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, 'aZb*cc777d')

# ################################################################################################################################

    def test_serialize_line_decimal_total_len_scale_value_error_has_dec_sep(self):

        with self.assertRaises(ValueError) as ctx:
            FWDecimal(2, 2, 'a')

        self.assertEquals(
            ctx.exception.message, 'Total length must be at least 3 if scale is 2 and a decimal separator is expected')

# ################################################################################################################################

    def test_serialize_line_decimal_total_len_scale_value_error_no_dec_sep(self):

        with self.assertRaises(ValueError) as ctx:
            FWDecimal(1, 2, 'a', has_dec_sep=False)

        self.assertEquals(
            ctx.exception.message, 'Total length must be at least 2 if scale is 2 and no decimal separator is expected')

# ################################################################################################################################

    def test_serialize_line_decimal_from_string_input(self):

        a = FWDecimal(4, 2, 'a')
        b = FWDecimal(5, 2, 'b')
        c = FWDecimal(6, 2, 'c')
        d = FWDecimal(7, 2, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = '1'
        response.b = '22'
        response.c = '333'
        response.d = '4444'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '1.0022.00333.004444.00')

# ################################################################################################################################

    def test_serialize_line_decimal_from_integer_input(self):

        a = FWDecimal(4, 2, 'a')
        b = FWDecimal(5, 2, 'b')
        c = FWDecimal(6, 2, 'c')
        d = FWDecimal(7, 2, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 1
        response.b = 22
        response.c = 333
        response.d = 4444

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '1.0022.00333.004444.00')

# ################################################################################################################################

    def test_serialize_line_decimal_from_long_input(self):

        a = FWDecimal(4, 2, 'a')
        b = FWDecimal(5, 2, 'b')
        c = FWDecimal(6, 2, 'c')
        d = FWDecimal(7, 2, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 1L
        response.b = 22L
        response.c = 333L
        response.d = 4444L

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '1.0022.00333.004444.00')

# ################################################################################################################################

    def test_serialize_line_decimal_from_float_input(self):

        a = FWDecimal(4, 2, 'a')
        b = FWDecimal(5, 2, 'b')
        c = FWDecimal(6, 2, 'c')
        d = FWDecimal(7, 2, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = 1.0
        response.b = 22.0
        response.c = 333.0
        response.d = 4444.0

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '1.0022.00333.004444.00')

# ################################################################################################################################

    def test_serialize_line_decimal_from_decimal_input(self):

        a = FWDecimal(4, 2, 'a')
        b = FWDecimal(5, 2, 'b')
        c = FWDecimal(6, 2, 'c')
        d = FWDecimal(7, 2, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = Decimal('1')
        response.b = Decimal('22')
        response.c = Decimal('333')
        response.d = Decimal('4444')

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '1.0022.00333.004444.00')

# ################################################################################################################################

    def test_serialize_line_decimal_from_decimal_input_quantize_scale(self):

        a = FWDecimal(4, 2, 'a')
        b = FWDecimal(5, 2, 'b')
        c = FWDecimal(6, 2, 'c')
        d = FWDecimal(7, 2, 'd')
        definition = (a, b, c, d)

        response = Bunch()
        response.a = Decimal('1.1')
        response.b = Decimal('22.22')
        response.c = Decimal('333.3333')
        response.d = Decimal('4444.4444')

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '1.1022.22333.334444.44')

# ################################################################################################################################

    def test_serialize_line_timestamp_from_string_input(self):

        a = Timestamp(26, 'a')
        b = Timestamp(36, 'b')
        definition = (a, b)

        response = Bunch()
        response.a = '2017-01-25T21:30:53.020669'
        response.b = '2018-02-26T22:31:54.131770'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '2017-01-25T21:30:53.0206692018-02-26T22:31:54.131770          ')

# ################################################################################################################################

    def test_serialize_line_timestamp_from_datetime_input(self):

        a = Timestamp(26, 'a')
        b = Timestamp(36, 'b')
        definition = (a, b)

        response = Bunch()
        response.a = datetime_datetime(2017, 1, 25, 21, 30, 53, 20669)
        response.b = datetime_datetime(2018, 2, 26, 22, 31, 54, 131770)

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '2017-01-25T21:30:53.0206692018-02-26T22:31:54.131770          ')

# ################################################################################################################################

    def test_serialize_line_timestamp_from_string_input_with_output_format(self):

        a = Timestamp(30, 'a', '%y/%m/%j-(%U)-%I--%M--%S')
        b = Timestamp(30, 'b', '%y/%m/%j-(%U)-%I--%M--%S')
        definition = (a, b)

        response = Bunch()
        response.a = '2017-01-25T21:30:53.020669'
        response.b = '2018-02-26T22:31:54.131770'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '17/01/025-(04)-09--30--53     18/02/057-(08)-10--31--54     ')

# ################################################################################################################################

    def test_serialize_line_timestamp_from_datetime_input_with_output_format(self):

        a = Timestamp(30, 'a', '%y/%m/%j-(%U)-%I--%M--%S')
        b = Timestamp(30, 'b', '%y/%m/%j-(%U)-%I--%M--%S')
        definition = (a, b)

        response = Bunch()
        response.a = datetime_datetime(2017, 1, 25, 21, 30, 53, 20669)
        response.b = datetime_datetime(2018, 2, 26, 22, 31, 54, 131770)

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '17/01/025-(04)-09--30--53     18/02/057-(08)-10--31--54     ')

# ################################################################################################################################

    def test_serialize_line_date_from_string_input(self):

        a = Date(16, 'a')
        b = Date(16, 'b')
        definition = (a, b)

        response = Bunch()
        response.a = '2017-01-25'
        response.b = '2018-02-26'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '2017-01-25      2018-02-26      ')

# ################################################################################################################################

    def test_serialize_line_date_from_date_input(self):

        a = Date(16, 'a')
        b = Date(16, 'b')
        definition = (a, b)

        response = Bunch()
        response.a = datetime_date(2017, 1, 25)
        response.b = datetime_date(2018, 2, 26)

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '2017-01-25      2018-02-26      ')

# ################################################################################################################################

    def test_serialize_line_date_from_string_input_with_output_format(self):

        a = Date(12, 'a', '%m-%d-%y')
        b = Date(12, 'b', '%m-%d-%y')
        definition = (a, b)

        response = Bunch()
        response.a = '2017-01-25'
        response.b = '2018-02-26'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '01-25-17    02-26-18    ')

# ################################################################################################################################

    def test_serialize_line_date_from_date_input_with_output_format(self):

        a = Date(12, 'a', '%m-%d-%y')
        b = Date(12, 'b', '%m-%d-%y')
        definition = (a, b)

        response = Bunch()
        response.a = datetime_date(2017, 1, 25)
        response.b = datetime_date(2018, 2, 26)

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '01-25-17    02-26-18    ')

# ################################################################################################################################

    def test_serialize_line_time_from_string_input(self):

        a = Time(16, 'a')
        b = Time(16, 'b')
        definition = (a, b)

        response = Bunch()
        response.a = '15:39'
        response.b = '23:33'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '15:39           23:33           ')

# ################################################################################################################################

    def test_serialize_line_time_from_date_input(self):

        a = Time(16, 'a')
        b = Time(16, 'b')
        definition = (a, b)

        response = Bunch()
        response.a = datetime_time(15, 39, 1)
        response.b = datetime_time(23, 33, 44)

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '15:39:01        23:33:44        ')

# ################################################################################################################################

    def test_serialize_line_time_from_string_input_with_output_format(self):

        a = Time(12, 'a', '%I--%M//%S')
        b = Time(12, 'b', '%I--%M//%S')
        definition = (a, b)

        response = Bunch()
        response.a = '15:39:01'
        response.b = '23:33:44'

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '03--39//01  11--33//44  ')

# ################################################################################################################################

    def test_serialize_line_time_from_date_input_with_output_format(self):

        a = Time(12, 'a', '%I--%M//%S')
        b = Time(12, 'b', '%I--%M//%S')
        definition = (a, b)

        response = Bunch()
        response.a = datetime_time(15, 39, 1)
        response.b = datetime_time(23, 33, 44)

        fw = FixedWidth(definition)
        result = fw.serialize(response)
        self.assertEquals(result, '03--39//01  11--33//44  ')

# ################################################################################################################################
