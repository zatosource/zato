# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from decimal import Decimal as decimal_Decimal, getcontext
from uuid import UUID as uuid_UUID

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.test import BaseSIOTestCase

# Zato - Cython
from zato.simpleio import AsIs, Bool,  CSV, Date, DateTime, Decimal, Dict, DictList, Float, Int, List, NotGiven, Opaque, \
     Text, UUID
from zato.util_convert import false_values, true_values

# Python 2/3 compatibility
from past.builtins import basestring, long, unicode

# ################################################################################################################################
# ################################################################################################################################

class ElemsFromJSONTestCase(BaseSIOTestCase):

# ################################################################################################################################

    def _parse(self, sio_elem, data):
        return sio_elem.parse_from[DATA_FORMAT.JSON](data)

# ################################################################################################################################

    def xtest_as_is(self):
        sio = AsIs('myname')
        data = object()
        parsed = self._parse(sio, data)

        self.assertIs(data, parsed)

# ################################################################################################################################

    def xtest_bool_true(self):
        sio = AsIs('myname')

        for data in true_values + tuple(elem.upper() for elem in true_values) + (True, 1, -1):
            parsed = self._parse(sio, data)
            self.assertTrue(parsed)

# ################################################################################################################################

    def xtest_bool_false(self):
        sio = Bool('myname')

        for data in false_values + tuple(elem.upper() for elem in false_values) + (False, 0):
            parsed = self._parse(sio, data)
            self.assertFalse(parsed)

# ################################################################################################################################

    def xtest_csv(self):
        sio = CSV('myname')
        data = 'q,w,e,r,t,Y,U,I,O,P'
        parsed = self._parse(sio, data)
        self.assertListEqual(parsed, data.split(','))

# ################################################################################################################################

    def xtest_date_valid(self):
        sio = Date('myname')
        year = 1999
        month = 12
        day = 31
        data = '{}-{}-{}'.format(day, month, year)
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, datetime)
        self.assertEquals(parsed.year, year)
        self.assertEquals(parsed.month, month)
        self.assertEquals(parsed.day, day)

# ################################################################################################################################

    def xtest_date_invalid(self):
        sio = Date('myname')
        year = 1999
        month = 77
        day = 31
        data = '{}-{}-{}'.format(day, month, year)

        with self.assertRaises(ValueError) as ctx:
            self._parse(sio, data)

        expected = 'Could not parse `31-77-1999` as a Date object (month must be in 1..12)'
        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def xtest_date_time_valid(self):
        sio = DateTime('myname')
        year = 1999
        month = 12
        day = 31
        hour = 11
        minute = 22
        second = 33
        data = '{}-{}-{}T{}:{}:{}.000Z'.format(day, month, year, hour, minute, second)
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, datetime)
        self.assertEquals(parsed.year, year)
        self.assertEquals(parsed.month, month)
        self.assertEquals(parsed.day, day)
        self.assertEquals(parsed.hour, hour)
        self.assertEquals(parsed.minute, minute)
        self.assertEquals(parsed.second, second)

# ################################################################################################################################

    def xtest_date_time_invalid(self):
        sio = DateTime('myname')
        year = 1999
        month = 12
        day = 31
        hour = 11
        minute = 22
        second = 99
        data = '{}-{}-{}T{}:{}:{}.000Z'.format(day, month, year, hour, minute, second)

        with self.assertRaises(ValueError) as ctx:
            self._parse(sio, data)

        expected = 'Could not parse `31-12-1999T11:22:99.000Z` as a DateTime object (second must be in 0..59)'
        self.assertEquals(ctx.exception.args[0], expected)

# ################################################################################################################################

    def xtest_decimal(self):

        sio = Decimal('mykey')

        exponent = '123456789' * 30
        data = '0.' + exponent
        getcontext().prec = 37

        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, decimal_Decimal)
        self.assertEquals(str(parsed), data)

# ################################################################################################################################

    def xtest_dict_without_key_names(self):

        sio = Dict('mykey')

        # Note that the dict will not expect any keys in particular on input because it has only a name and nothing else
        data = {
            'aaa': 'aaa-111',
            'bbb': 'bbb-111',
            'ccc': 'ccc-111',
            'ddd': 'ddd-111',
            'fff': 'fff-111'
        }
        parsed = self._parse(sio, data)

        self.assertDictEqual(parsed, data)

# ################################################################################################################################

    def xtest_dict_with_key_names(self):

        sio = Dict('mykey', 'aaa', 'bbb', 'ccc', '-ddd', '-eee')

        # Note that 'eee' is optional hence it may be omitted and that 'fff' is not part of the dict's I/O definition
        data = {
            'aaa': 'aaa-111',
            'bbb': 'bbb-111',
            'ccc': 'ccc-111',
            'ddd': 'ddd-111',
            'fff': 'fff-111'
        }
        parsed = self._parse(sio, data)

        self.assertDictEqual(parsed, {
            'aaa': 'aaa-111',
            'bbb': 'bbb-111',
            'ccc': 'ccc-111',
            'ddd': 'ddd-111',
            'eee': NotGiven,
        })

# ################################################################################################################################

    def xtest_dict_list_with_key_names(self):

        sio = DictList('mykey')

        data1 = {
            'aaa': 'aaa-111',
            'bbb': 'bbb-111',
            'ccc': 'ccc-111',
            'ddd': 'ddd-111',
            'fff': 'fff-111'
        }

        data2 = {
            'aaa': 'aaa-222',
            'bbb': 'bbb-222',
            'ccc': 'ccc-222',
            'ddd': 'ddd-222',
            'fff': 'fff-222'
        }

        data = [data1, data2]
        parsed = self._parse(sio, data)

        self.assertDictEqual(parsed[0], data1)
        self.assertDictEqual(parsed[1], data2)

# ################################################################################################################################

    def xtest_dict_list_without_key_names(self):

        sio = DictList('mykey', 'aaa', '-bbb', '-ccc')

        data1 = {
            'aaa': 'aaa-111',
            'bbb': 'bbb-111',
        }

        data2 = {
            'aaa': 'aaa-222',
            'bbb': 'bbb-222',
        }

        expected1 = {
            'aaa': 'aaa-111',
            'bbb': 'bbb-111',
            'ccc': NotGiven,
        }

        expected2 = {
            'aaa': 'aaa-222',
            'bbb': 'bbb-222',
            'ccc': NotGiven,
        }

        data = [data1, data2]
        parsed = self._parse(sio, data)

        self.assertDictEqual(parsed[0], expected1)
        self.assertDictEqual(parsed[1], expected2)

# ################################################################################################################################

    def xtest_list_from_list(self):
        sio = List('myname')
        data = ['q,w,e,r,t,Y,U,I,O,P']
        parsed = self._parse(sio, data)
        self.assertListEqual(parsed, data)

# ################################################################################################################################

    def xtest_float(self):
        sio = Float('myname')
        data = '1.23'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, float)
        self.assertEquals(parsed, 1.23)

# ################################################################################################################################

    def xtest_int(self):
        sio = Int('myname')
        data = '12345678901234567890'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, (int, long))
        self.assertEquals(parsed, int(data))

# ################################################################################################################################

    def xtest_list_from_tuple(self):
        sio = List('myname')
        data = tuple(['q,w,e,r,t,Y,U,I,O,P'])
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, tuple)
        self.assertEquals(parsed, data)

# ################################################################################################################################

    def xtest_list_from_string(self):
        sio = List('myname')
        data = 'abcdef'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, list)
        self.assertEquals(parsed, [data])

# ################################################################################################################################

    def xtest_list_from_int(self):
        sio = List('myname')
        data = 123
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, list)
        self.assertEquals(parsed, [data])

# ################################################################################################################################

    def xtest_opaque(self):

        class MyClass:
            pass

        sio = Opaque('myname')
        data = MyClass()
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, MyClass)
        self.assertIs(parsed, data)

# ################################################################################################################################

    def test_text(self):

        sio = Text('myname')
        data = 123
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, basestring)
        self.assertEquals(parsed, unicode(data))

# ################################################################################################################################

    def xtest_uuid(self):

        sio = UUID('myname')
        data = 'e9c56bde-fab4-4adb-96c1-479c8246f308'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, uuid_UUID)
        self.assertEquals(str(parsed), data)

# ################################################################################################################################
# ################################################################################################################################
