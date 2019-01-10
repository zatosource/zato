# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from decimal import Decimal as decimal_Decimal, getcontext
from json import dumps, loads
from unittest import TestCase
from uuid import UUID as uuid_UUID, uuid4

# dateutil
from dateutil.parser import parse as dt_parse

# Zato
from zato.common import DATA_FORMAT
from zato.server.service import Service
from zato.simpleio import backward_compat_default_value, AsIs, Bool, BoolConfig, CSV, CySimpleIO, Date, DateTime, Decimal, \
     Dict, DictList, Float, Int, IntConfig, List, NotGiven, Opaque, SecretConfig, _SIOServerConfig, Text, UUID

# Zato - Cython
from zato.util_convert import false_values, to_bool, true_values
from zato.bunch import Bunch, bunchify

# ################################################################################################################################
# ################################################################################################################################

class _BaseTestCase(TestCase):

    def get_server_config(self):

        SIOServerConfig = _SIOServerConfig()
        server_config = Bunch()

        server_config.bool = Bunch()
        server_config.bool.exact  = set()
        server_config.bool.prefix = set(['by_', 'has_', 'is_', 'may_', 'needs_', 'should_'])
        server_config.bool.suffix = set()

        server_config.int = Bunch()
        server_config.int.exact  = set(['id'])
        server_config.int.prefix = set()
        server_config.int.suffix = set(['_count', '_id', '_size', '_timeout'])

        server_config.secret = Bunch()
        server_config.secret.exact  = set(['id'])
        server_config.secret.prefix = set(
            ['auth_data', 'auth_token', 'password', 'password1', 'password2', 'secret_key', 'token'])
        server_config.secret.suffix = set()

        server_config.default = Bunch()

        server_config.default.default_value = None
        server_config.default.default_input_value = None
        server_config.default.default_output_value = None

        server_config.default.response_elem = None

        server_config.default.input_required_name = 'input_required'
        server_config.default.input_optional_name = 'input_optional'
        server_config.default.output_required_name = 'output_required'
        server_config.default.output_optional_name = 'output_optional'

        server_config.default.skip_empty_keys = False
        server_config.default.skip_empty_request_keys = False
        server_config.default.skip_empty_response_keys = False

        server_config.default.prefix_as_is = 'a'
        server_config.default.prefix_bool = 'b'
        server_config.default.prefix_csv = 'c'
        server_config.default.prefix_date = 'date'
        server_config.default.prefix_date_time = 'dt'
        server_config.default.prefix_dict = 'd'
        server_config.default.prefix_dict_list = 'dl'
        server_config.default.prefix_float = 'f'
        server_config.default.prefix_int = 'i'
        server_config.default.prefix_list = 'l'
        server_config.default.prefix_opaque = 'o'
        server_config.default.prefix_text = 't'
        server_config.default.prefix_uuid = 'u'

        bool_config = BoolConfig()
        bool_config.exact = server_config.bool.exact
        bool_config.prefixes = server_config.bool.prefix
        bool_config.suffixes = server_config.bool.suffix

        int_config = IntConfig()
        int_config.exact = server_config.int.exact
        int_config.prefixes = server_config.int.prefix
        int_config.suffixes = server_config.int.suffix

        secret_config = SecretConfig()
        secret_config.exact = server_config.secret.exact
        secret_config.prefixes = server_config.secret.prefix
        secret_config.suffixes = server_config.secret.suffix

        SIOServerConfig.bool_config = bool_config
        SIOServerConfig.int_config = int_config
        SIOServerConfig.secret_config = secret_config

        SIOServerConfig.input_required_name = server_config.default.input_required_name
        SIOServerConfig.input_optional_name = server_config.default.input_optional_name
        SIOServerConfig.output_required_name = server_config.default.output_required_name
        SIOServerConfig.output_optional_name = server_config.default.output_optional_name
        SIOServerConfig.default_value = server_config.default.default_value
        SIOServerConfig.default_input_value = server_config.default.default_input_value
        SIOServerConfig.default_output_value = server_config.default.default_output_value

        SIOServerConfig.response_elem = server_config.default.response_elem

        SIOServerConfig.skip_empty_keys = server_config.default.skip_empty_keys
        SIOServerConfig.skip_empty_request_keys = server_config.default.skip_empty_request_keys
        SIOServerConfig.skip_empty_response_keys = server_config.default.skip_empty_response_keys

        SIOServerConfig.prefix_as_is = server_config.default.prefix_as_is
        SIOServerConfig.prefix_bool = server_config.default.prefix_bool
        SIOServerConfig.prefix_csv = server_config.default.prefix_csv
        SIOServerConfig.prefix_date = server_config.default.prefix_date
        SIOServerConfig.prefix_date_time = server_config.default.prefix_date_time
        SIOServerConfig.prefix_dict = server_config.default.prefix_dict
        SIOServerConfig.prefix_dict_list = server_config.default.prefix_dict_list
        SIOServerConfig.prefix_float = server_config.default.prefix_float
        SIOServerConfig.prefix_int = server_config.default.prefix_int
        SIOServerConfig.prefix_list = server_config.default.prefix_list
        SIOServerConfig.prefix_opaque = server_config.default.prefix_opaque
        SIOServerConfig.prefix_text = server_config.default.prefix_text
        SIOServerConfig.prefix_uuid = server_config.default.prefix_uuid

        return SIOServerConfig

    def get_sio(self, declaration):

        sio = CySimpleIO(self.get_server_config(), declaration)
        sio.build()

        return sio

# ################################################################################################################################
# ################################################################################################################################

class InputOutputParsingTestCase(_BaseTestCase):

    def test_no_input_output(self):

        class SimpleIO:
            pass

        # Providing such a bare declaration should not raise an exceptions
        self.get_sio(SimpleIO)

# ################################################################################################################################

    def test_input_and_input_required_error(self):

        class SimpleIO:
            input = 'qwerty'
            input_required = 'aaa', 'bbb'

        # Cannot have both input and input_required on input
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Cannot provide input_required if input is given, input:`qwerty`, " \
            "input_required:`(u'aaa', u'bbb')`, input_optional:`[]`"

        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_input_and_input_optional_error(self):

        class SimpleIO:
            input = 'qwerty'
            input_optional = 'aaa', 'bbb'

        # Cannot have both input and input_required on input
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Cannot provide input_optional if input is given, input:`qwerty`, " \
            "input_required:`[]`, input_optional:`(u'aaa', u'bbb')`"

        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_input_and_input_required_optional_error(self):

        class SimpleIO:
            input = 'qwerty'
            input_required = '123', '456'
            input_optional = 'aaa', 'bbb'

        # Cannot have both input and input_required on input
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Cannot provide input_required/input_optional if input is given, input:`qwerty`, " \
            "input_required:`(u'123', u'456')`, input_optional:`(u'aaa', u'bbb')`"

        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_output_and_output_required_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_required = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Cannot provide output_required if output is given, output:`qwerty`, " \
            "output_required:`(u'aaa', u'bbb')`, output_optional:`[]`"

        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_output_and_output_optional_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_optional = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Cannot provide output_optional if output is given, output:`qwerty`, " \
            "output_required:`[]`, output_optional:`(u'aaa', u'bbb')`"

        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_output_and_output_required_optional_error(self):

        class SimpleIO:
            output = 'qwerty'
            output_required = '123', '456'
            output_optional = 'aaa', 'bbb'

        # Cannot have both output and output_required on output
        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Cannot provide output_required/output_optional if output is given, output:`qwerty`, " \
            "output_required:`(u'123', u'456')`, output_optional:`(u'aaa', u'bbb')`"

        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_elem_sharing_not_allowed(self):

        class SimpleIO:
            input_required = 'abc', 'zxc', 'qwe'
            input_optional = 'zxc', 'abc', 'rty'

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Elements in input_required and input_optional cannot be shared, found:`['abc', 'zxc']`"
        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_default_input_value(self):

        class SimpleIO:
            input_required = 'abc', 'zxc', 'qwe'
            input_optional = 'zxc', 'abc', 'rty'

        with self.assertRaises(ValueError) as ctx:
            self.get_sio(SimpleIO)

        expected = "Elements in input_required and input_optional cannot be shared, found:`['abc', 'zxc']`"
        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################
# ################################################################################################################################

class InputPlainParsingTestCase(_BaseTestCase):

    def test_convert_plain_into_required_optional(self):

        class SimpleIO:
            input = 'abc', 'zxc', 'ghj', '-rrr', '-eee'
            output = 'abc2', 'zxc2', 'ghj2', '-rrr2', '-eee2'

        sio = self.get_sio(SimpleIO)

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
            self.get_sio(SimpleIO)

        expected = "Elements in input_required and input_optional cannot be shared, found:`['abc', 'zxc']`"
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

class AttachSIOTestCase(_BaseTestCase):
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

class ElemsFromJSONTestCase(_BaseTestCase):

# ################################################################################################################################

    def _parse(self, sio_elem, data):
        return sio_elem.parse_from[DATA_FORMAT.JSON](data)

# ################################################################################################################################

    def test_as_is(self):
        sio = AsIs('myname')
        data = object()
        parsed = self._parse(sio, data)

        self.assertIs(data, parsed)

# ################################################################################################################################

    def test_bool_true(self):
        sio = AsIs('myname')

        for data in true_values + tuple(elem.upper() for elem in true_values) + (True, 1, -1):
            parsed = self._parse(sio, data)
            self.assertTrue(parsed)

# ################################################################################################################################

    def test_bool_false(self):
        sio = Bool('myname')

        for data in false_values + tuple(elem.upper() for elem in false_values) + (False, 0):
            parsed = self._parse(sio, data)
            self.assertFalse(parsed)

# ################################################################################################################################

    def test_csv(self):
        sio = CSV('myname')
        data = 'q,w,e,r,t,Y,U,I,O,P'
        parsed = self._parse(sio, data)
        self.assertListEqual(parsed, data.split(','))

# ################################################################################################################################

    def test_date_valid(self):
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

    def test_date_invalid(self):
        sio = Date('myname')
        year = 1999
        month = 77
        day = 31
        data = '{}-{}-{}'.format(day, month, year)

        with self.assertRaises(ValueError) as ctx:
            self._parse(sio, data)

        expected = 'Could not parse `31-77-1999` as a Date object (month must be in 1..12)'
        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_date_time_valid(self):
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

    def test_date_time_invalid(self):
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
        self.assertEquals(ctx.exception.message, expected)

# ################################################################################################################################

    def test_decimal(self):

        sio = Decimal('mykey')

        exponent = '123456789' * 30
        data = '0.' + exponent
        getcontext().prec = 37

        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, decimal_Decimal)
        self.assertEquals(str(parsed), data)

# ################################################################################################################################

    def test_dict_without_key_names(self):

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

    def test_dict_with_key_names(self):

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

    def test_dict_list_with_key_names(self):

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

    def test_dict_list_without_key_names(self):

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

    def test_list_from_list(self):
        sio = List('myname')
        data = ['q,w,e,r,t,Y,U,I,O,P']
        parsed = self._parse(sio, data)
        self.assertListEqual(parsed, data)

# ################################################################################################################################

    def test_float(self):
        sio = Float('myname')
        data = '1.23'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, float)
        self.assertEquals(parsed, 1.23)

# ################################################################################################################################

    def test_int(self):
        sio = Int('myname')
        data = '12345678901234567890'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, (int, long))
        self.assertEquals(parsed, int(data))

# ################################################################################################################################

    def test_list_from_tuple(self):
        sio = List('myname')
        data = tuple(['q,w,e,r,t,Y,U,I,O,P'])
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, tuple)
        self.assertEquals(parsed, data)

# ################################################################################################################################

    def test_list_from_string(self):
        sio = List('myname')
        data = 'abcdef'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, list)
        self.assertEquals(parsed, [data])

# ################################################################################################################################

    def test_list_from_int(self):
        sio = List('myname')
        data = 123
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, list)
        self.assertEquals(parsed, [data])

# ################################################################################################################################

    def test_opaque(self):

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

    def test_uuid(self):

        sio = UUID('myname')
        data = 'e9c56bde-fab4-4adb-96c1-479c8246f308'
        parsed = self._parse(sio, data)

        self.assertIsInstance(parsed, uuid_UUID)
        self.assertEquals(str(parsed), data)

# ################################################################################################################################
# ################################################################################################################################

class JSONInputParsing(_BaseTestCase):

# ################################################################################################################################

    def test_parse_basic_request(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('bbb'), Opaque('ccc'), '-ddd', '-eee'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = '222'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'bbb': bbb,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)

        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, int(bbb))
        self.assertIs(input.ccc, ccc)
        self.assertEquals(input.ddd, backward_compat_default_value)
        self.assertEquals(input.eee, eee)

# ################################################################################################################################

    def test_parse_all_elem_types_non_list(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', AsIs('bbb'), Bool('ccc'), CSV('ddd'), Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Dict('hhh', 'a', 'b', 'c'), DictList('iii', 'd', 'e', 'f'), Float('jjj'), Int('mmm'), List('nnn'), \
                    Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = object()
        ccc = True
        ddd = '1,2,3,4'
        eee = '1999-12-31'
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'
        hhh = {'a':1, 'b':2, 'c':3}
        iii = [{'d':4, 'e':5, 'f':6}, {'d':44, 'e':55, 'f':66}]
        jjj = '111.222'
        mmm = '9090'
        nnn = [1, 2, 3, 4]
        ooo = object()
        ppp = 'mytext'
        qqq = 'd011d054-db4b-4320-9e24-7f4c217af673'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'bbb': bbb,
            'ccc': ccc,
            'ddd': ddd,
            'eee': eee,
            'fff': fff,
            'ggg': ggg,
            'hhh': hhh,
            'iii': iii,
            'jjj': jjj,
            'mmm': mmm,
            'nnn': nnn,
            'ooo': ooo,
            'ppp': ppp,
            'qqq': qqq,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, aaa)
        self.assertIs(input.bbb, bbb)
        self.assertTrue(input.ccc)
        self.assertListEqual(input.ddd, ['1', '2', '3', '4'])

        self.assertIsInstance(input.eee, datetime)
        self.assertEquals(input.eee.year, 1999)
        self.assertEquals(input.eee.month, 12)
        self.assertEquals(input.eee.day, 31)

        self.assertIsInstance(input.fff, datetime)
        self.assertEquals(input.fff.year, 1988)
        self.assertEquals(input.fff.month, 01)
        self.assertEquals(input.fff.day, 29)

# ################################################################################################################################

    def test_parse_all_elem_types_list(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', AsIs('bbb'), Bool('ccc'), CSV('ddd'), Date('eee'), DateTime('fff'), Decimal('ggg'), \
                    Dict('hhh', 'a', 'b', 'c'), DictList('iii', 'd', 'e', 'f'), Float('jjj'), Int('mmm'), List('nnn'), \
                    Opaque('ooo'), Text('ppp'), UUID('qqq')

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        bbb = object()
        ccc = True
        ddd = '1,2,3,4'
        eee = '1999-12-31'
        fff = '1988-01-29T11:22:33.0000Z'
        ggg = '123.456'
        hhh = {'a':1, 'b':2, 'c':3}
        iii = [{'d':4, 'e':5, 'f':6}, {'d':44, 'e':55, 'f':66}]
        jjj = '111.222'
        mmm = '9090'
        nnn = [1, 2, 3, 4]
        ooo = object()
        ppp = 'mytext'
        qqq = 'd011d054-db4b-4320-9e24-7f4c217af673'

        aaa2 = 'aaa-222'
        bbb2 = object()
        ccc2 = False
        ddd2 = '5,6,7,8'
        eee2 = '1999-12-25'
        fff2 = '1977-01-29T11:22:33.0000Z'
        ggg2 = '999.777'
        hhh2 = {'a':12, 'b':22, 'c':32}
        iii2 = [{'d':42, 'e':52, 'f':62}, {'d':442, 'e':552, 'f':662}]
        jjj2 = '333.444'
        mmm2 = '7171'
        nnn2 = [5, 6, 7, 8]
        ooo2 = object()
        ppp2 = 'mytext2'
        qqq2 = 'd011d054-db4b-4320-9e24-7f4c217af672'

        # Note that 'ddd' is optional and we are free to skip it
        data = [{
            'aaa': aaa,
            'bbb': bbb,
            'ccc': ccc,
            'ddd': ddd,
            'eee': eee,
            'fff': fff,
            'ggg': ggg,
            'hhh': hhh,
            'iii': iii,
            'jjj': jjj,
            'mmm': mmm,
            'nnn': nnn,
            'ooo': ooo,
            'ppp': ppp,
            'qqq': qqq,
        },
        {
            'aaa': aaa2,
            'bbb': bbb2,
            'ccc': ccc2,
            'ddd': ddd2,
            'eee': eee2,
            'fff': fff2,
            'ggg': ggg2,
            'hhh': hhh2,
            'iii': iii2,
            'jjj': jjj2,
            'mmm': mmm2,
            'nnn': nnn2,
            'ooo': ooo2,
            'ppp': ppp2,
            'qqq': qqq2,
        }]

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)

        self.assertIsInstance(input, list)
        self.assertEquals(len(input), 2)

        input1 = input[0]
        input2 = input[1]

        self.assertEquals(input1.aaa, aaa)
        self.assertIs(input1.bbb, bbb)
        self.assertTrue(input1.ccc)
        self.assertListEqual(input1.ddd, ['1', '2', '3', '4'])

        self.assertIsInstance(input1.eee, datetime)
        self.assertEquals(input1.eee.year, 1999)
        self.assertEquals(input1.eee.month, 12)
        self.assertEquals(input1.eee.day, 31)

        self.assertIsInstance(input1.fff, datetime)
        self.assertEquals(input1.fff.year, 1988)
        self.assertEquals(input1.fff.month, 01)
        self.assertEquals(input1.fff.day, 29)
        self.assertEquals(input1.fff.hour, 11)
        self.assertEquals(input1.fff.minute, 22)
        self.assertEquals(input1.fff.second, 33)

        self.assertEquals(input2.aaa, aaa2)
        self.assertIs(input2.bbb, bbb2)
        self.assertFalse(input2.ccc)
        self.assertListEqual(input2.ddd, ['5', '6', '7', '8'])

        self.assertIsInstance(input2.eee, datetime)
        self.assertEquals(input2.eee.year, 1999)
        self.assertEquals(input2.eee.month, 12)
        self.assertEquals(input2.eee.day, 25)

        self.assertIsInstance(input2.fff, datetime)
        self.assertEquals(input2.fff.year, 1977)
        self.assertEquals(input2.fff.month, 01)
        self.assertEquals(input2.fff.day, 29)
        self.assertEquals(input2.fff.hour, 11)
        self.assertEquals(input2.fff.minute, 22)
        self.assertEquals(input2.fff.second, 33)

# ################################################################################################################################

    def test_parse_default_with_default_input_value(self):

        _default_bbb = 112233
        _default_fff = object()
        _default_input_value = object()

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('-bbb', default=_default_bbb), Opaque('ccc'), '-ddd', Text('-eee'), \
                    Text('-fff', default=_default_fff)
                default_input_value = _default_input_value

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, _default_bbb)
        self.assertIs(input.ccc, ccc)
        self.assertEquals(input.ddd, _default_input_value)
        self.assertEquals(input.eee, eee)
        self.assertEquals(input.fff, _default_fff)

# ################################################################################################################################

    def test_parse_default_no_default_input_value(self):

        _default_bbb = 112233
        _default_fff = object()
        _default_input_value = object()

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('-bbb', default=_default_bbb), Opaque('ccc'), '-ddd', Text('-eee'), \
                    Text('-fff', default=_default_fff)

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, _default_bbb)
        self.assertIs(input.ccc, ccc)
        self.assertEquals(input.ddd, backward_compat_default_value)
        self.assertEquals(input.eee, eee)
        self.assertEquals(input.fff, _default_fff)

# ################################################################################################################################

    def test_parse_default_backward_compat_default_input_value(self):

        _default_bbb = 112233
        _default_fff = object()
        _default_input_value = object()

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', Int('-bbb', default=_default_bbb), Opaque('ccc'), '-ddd', Text('-eee'), \
                    Text('-fff', default=_default_fff)
                default_value = _default_input_value

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        aaa = 'aaa-111'
        ccc = object()
        eee = 'eee-111'

        # Note that 'ddd' is optional and we are free to skip it
        data = {
            'aaa': aaa,
            'ccc': ccc,
            'eee': eee,
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, aaa)
        self.assertEquals(input.bbb, _default_bbb)
        self.assertIs(input.ccc, ccc)
        self.assertEquals(input.ddd, _default_input_value)
        self.assertEquals(input.eee, eee)
        self.assertEquals(input.fff, _default_fff)

# ################################################################################################################################

    def test_parse_default_all_elem_types(self):

        bbb = object()
        ccc = False
        ddd = [1, 2, 3, 4]
        eee = datetime(year=1990, month=1, day=29)
        fff = datetime(year=1990, month=1, day=29, hour=1, minute=2, second=3)
        ggg = decimal_Decimal('12.34')
        hhh = {'a':1, 'b':2, 'c':3}
        iii = [{'a':1, 'b':2, 'c':3}, {'a':11, 'b':22, 'c':33}]
        jjj = 99.77
        mmm = 123
        nnn = ['a', 'b', 'c']
        ooo = object()
        ppp = 'mytext'
        qqq = uuid4().hex

        class MyService(Service):
            class SimpleIO:
                input = '-aaa', AsIs('-bbb', default=bbb), Bool('-ccc', default=ccc), CSV('-ddd', default=ddd), \
                    Date('-eee', default=eee), DateTime('-fff', default=fff), Decimal('-ggg', default=ggg), \
                    Dict('-hhh', 'a', 'b', 'c', default=hhh), DictList('-iii', 'd', 'e', 'f', default=iii), \
                    Float('-jjj', default=jjj), Int('-mmm', default=mmm), List('-nnn', default=nnn), \
                    Opaque('-ooo', default=ooo), Text('-ppp', default=ppp), UUID('-qqq', default=qqq)

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        # Note that the input document is empty
        input = MyService._sio.parse_input({}, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa, backward_compat_default_value)
        self.assertEquals(input.bbb, bbb)
        self.assertEquals(input.ccc, ccc)
        self.assertEquals(input.ddd, ddd)
        self.assertEquals(input.eee, eee)
        self.assertEquals(input.fff, fff)
        self.assertEquals(input.ggg, ggg)
        self.assertEquals(input.hhh, hhh)
        self.assertEquals(input.iii, iii)
        self.assertEquals(input.jjj, jjj)
        self.assertEquals(input.mmm, mmm)
        self.assertEquals(input.nnn, nnn)
        self.assertEquals(input.ooo, ooo)
        self.assertEquals(input.ppp, ppp)
        self.assertEquals(input.qqq, qqq)

# ################################################################################################################################

    def test_parse_nested_dict_only_default_sio_level(self):

        _default_input_value = 'default-input-value'

        aaa = 'aaa'
        bbb = 'bbb'
        ccc = Dict('ccc', 'ddd', 'eee', '-fff')
        sss = Dict('sss', '-qqq')
        ggg = Dict('ggg', '-hhh', '-jjj', sss)

        class MyService(Service):
            class SimpleIO:
                input = Dict(aaa, bbb, ccc, ggg, '-ppp')
                default_input_value = _default_input_value

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        data = {
            'aaa': {
                'bbb': 'bbb-111',
                'ccc': {
                    'ddd': 'ddd-111',
                    'eee': 'eee-111',
                },
                'ggg': {
                    'sss': {}
                }
            }
        }

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.aaa.bbb, 'bbb-111')
        self.assertEquals(input.aaa.ccc.ddd, 'ddd-111')
        self.assertEquals(input.aaa.ccc.eee, 'eee-111')
        self.assertEquals(input.aaa.ccc.fff, _default_input_value)
        self.assertEquals(input.aaa.ccc.eee, 'eee-111')
        self.assertEquals(input.aaa.ggg.hhh, _default_input_value)
        self.assertEquals(input.aaa.ggg.sss.qqq, _default_input_value)

# ################################################################################################################################

    def test_parse_nested_dict_customer_no_defaults(self):

        locality = Dict('locality', 'type', 'name')
        address = Dict('address', locality, 'street')
        email = Dict('email', 'personal', 'business')
        customer = Dict('customer', 'name', email, address)

        class MyService(Service):
            class SimpleIO:
                input = customer

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.personal = 'my-personal-email'
        data.customer.email.business = 'my-business-email'
        data.customer.address = Bunch()
        data.customer.address.street = 'my-street'
        data.customer.address.locality = Bunch()
        data.customer.address.locality.type = 'my-type'
        data.customer.address.locality.name = 'my-name'

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.customer.name, data.customer.name)
        self.assertEquals(input.customer.email.personal, data.customer.email.personal)
        self.assertEquals(input.customer.email.business, data.customer.email.business)
        self.assertEquals(input.customer.address.street, data.customer.address.street)
        self.assertEquals(input.customer.address.locality.type, data.customer.address.locality.type)
        self.assertEquals(input.customer.address.locality.name, data.customer.address.locality.name)

# ################################################################################################################################

    def test_parse_nested_dict_customer_deep_defaults_sio_level(self):

        locality = Dict('locality', '-type', '-name')
        address = Dict('address', locality, 'street')
        email = Dict('email', 'personal', 'business')
        customer = Dict('customer', 'name', email, address)

        _default_input_value = 'default-input-value'

        class MyService(Service):
            class SimpleIO:
                input = customer
                default_input_value = 'default-input-value'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        # Note that locality has no type nor name and we expect for the SimpleIO-level default value to be used
        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.personal = 'my-personal-email'
        data.customer.email.business = 'my-business-email'
        data.customer.address = Bunch()
        data.customer.address.street = 'my-street'
        data.customer.address.locality = Bunch()

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.customer.name, data.customer.name)
        self.assertEquals(input.customer.email.personal, data.customer.email.personal)
        self.assertEquals(input.customer.email.business, data.customer.email.business)
        self.assertEquals(input.customer.address.street, data.customer.address.street)
        self.assertEquals(input.customer.address.locality.type, _default_input_value)
        self.assertEquals(input.customer.address.locality.name, _default_input_value)

# ################################################################################################################################

    def test_parse_nested_dict_customer_deep_defaults_elem_level(self):

        locality_default = object()

        locality = Dict('locality', '-type', '-name', default=locality_default)
        address = Dict('address', locality, '-street')
        email = Dict('email', 'personal', 'business')
        customer = Dict('customer', 'name', email, address)

        _default_input_value = 'default-input-value'

        class MyService(Service):
            class SimpleIO:
                input = customer
                default_input_value = 'default-input-value'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        # Note that this locality has no type nor name but we expect for that Dict's default value to be used,
        # also, address has no street but since this Dict has no default value, again, SimpleIO one will be used.
        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.personal = 'my-personal-email'
        data.customer.email.business = 'my-business-email'
        data.customer.address = Bunch()
        data.customer.address.locality = Bunch()

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.customer.name, data.customer.name)
        self.assertEquals(input.customer.email.personal, data.customer.email.personal)
        self.assertEquals(input.customer.email.business, data.customer.email.business)
        self.assertEquals(input.customer.address.street, _default_input_value)
        self.assertEquals(input.customer.address.locality.type, locality_default)
        self.assertEquals(input.customer.address.locality.name, locality_default)

# ################################################################################################################################

    def test_parse_nested_dict_all_sio_elems(self):

        locality = Dict('locality', Int('type'), Text('name'), AsIs('coords'), Decimal('geo_skip'), Float('geo_diff'))
        address = Dict('address', locality, UUID('street_id'), CSV('prefs'), DateTime('since'), List('types'), Opaque('opaque1'))
        email = Dict('email', Text('value'), Bool('is_business'), Date('join_date'), DictList('preferred_order', 'name', 'pos'))
        customer = Dict('customer', 'name', email, address)

        class MyService(Service):
            class SimpleIO:
                input = customer

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.value = 'my-email'
        data.customer.email.is_business = True
        data.customer.email.join_date = '1999-12-31'
        data.customer.email.preferred_order = [{'name':'address2', 'pos':'2'}, {'name':'address1', 'pos':'1'}]
        data.customer.address = Bunch()
        data.customer.address.locality = Bunch()
        data.customer.address.locality.type = '111'
        data.customer.address.locality.name = 'my-locality'
        data.customer.address.locality.coords = object()
        data.customer.address.locality.geo_skip = '123.456'
        data.customer.address.locality.geo_diff = '999.777'
        data.customer.address.street_id = uuid4().hex
        data.customer.address.prefs = '1,2,3,4'
        data.customer.address.since = '27-11-1988T11:22:33'
        data.customer.address.types = ['a', 'b', 'c', 'd']
        data.customer.address.opaque1 = object()

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.customer.name, data.customer.name)
        self.assertEquals(input.customer.email.value, data.customer.email.value)
        self.assertEquals(input.customer.email.is_business, data.customer.email.is_business)
        self.assertEquals(input.customer.email.join_date, dt_parse(data.customer.email.join_date))
        self.assertListEqual(input.customer.email.preferred_order, data.customer.email.preferred_order)
        self.assertEquals(input.customer.address.locality.type, int(data.customer.address.locality.type))
        self.assertEquals(input.customer.address.locality.name, data.customer.address.locality.name)
        self.assertIs(input.customer.address.locality.coords, data.customer.address.locality.coords)
        self.assertEquals(input.customer.address.locality.geo_skip, decimal_Decimal(data.customer.address.locality.geo_skip))
        self.assertEquals(input.customer.address.locality.geo_diff, float(data.customer.address.locality.geo_diff))
        self.assertEquals(input.customer.address.street_id, uuid_UUID(data.customer.address.street_id))
        self.assertEquals(input.customer.address.prefs, data.customer.address.prefs.split(','))
        self.assertEquals(input.customer.address.since, dt_parse(data.customer.address.since))
        self.assertEquals(input.customer.address.types, data.customer.address.types)
        self.assertIs(input.customer.address.opaque1, data.customer.address.opaque1)

# ################################################################################################################################

    def test_parse_nested_dict_all_sio_elems_some_missing(self):

        _default_input_value = 'default-input-value'
        default_locality = 'default-locality'
        default_address = 'default-address'

        locality = Dict('locality',
            Int('type'), Text('name'), AsIs('-coords'), Decimal('geo_skip'), Float('geo_diff'),
            default=default_locality)

        address = Dict('address',
            locality, UUID('-street_id'), CSV('prefs'), DateTime('since'), List('types'), Opaque('opaque1'),
            default=default_address)

        email = Dict('email', Text('value'), Bool('is_business'), Date('-join_date'), DictList('preferred_order', 'name', '-pos'))
        customer = Dict('customer', 'name', email, address)

        class MyService(Service):
            class SimpleIO:
                input = customer
                default_input_value = 'default-input-value'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        # Note that 'join_date', 'street_id', 'coords' and one of 'pos' keys are missing in input below,
        # the test ensures that default values are used in their place.

        data = Bunch()
        data.customer = Bunch()
        data.customer.name = 'my-name'
        data.customer.email = Bunch()
        data.customer.email.value = 'my-email'
        data.customer.email.is_business = True
        data.customer.email.preferred_order = [{'name':'address2', 'pos':'2'}, {'name':'address1'}]
        data.customer.address = Bunch()
        data.customer.address.locality = Bunch()
        data.customer.address.locality.type = '111'
        data.customer.address.locality.name = 'my-locality'
        data.customer.address.locality.geo_skip = '123.456'
        data.customer.address.locality.geo_diff = '999.777'
        data.customer.address.prefs = '1,2,3,4'
        data.customer.address.since = '27-11-1988T11:22:33'
        data.customer.address.types = ['a', 'b', 'c', 'd']
        data.customer.address.opaque1 = object()

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)

        self.assertEquals(input.customer.name, data.customer.name)
        self.assertEquals(input.customer.email.value, data.customer.email.value)
        self.assertEquals(input.customer.email.is_business, data.customer.email.is_business)
        self.assertEquals(input.customer.email.join_date, _default_input_value)

        self.assertDictEqual(input.customer.email.preferred_order[0], data.customer.email.preferred_order[0])
        self.assertEquals(input.customer.email.preferred_order[1].name, data.customer.email.preferred_order[1]['name'])
        self.assertEquals(input.customer.email.preferred_order[1].pos, _default_input_value)

        self.assertEquals(input.customer.address.locality.type, int(data.customer.address.locality.type))
        self.assertEquals(input.customer.address.locality.name, data.customer.address.locality.name)
        self.assertEquals(input.customer.address.locality.coords, default_locality)
        self.assertEquals(input.customer.address.locality.geo_skip, decimal_Decimal(data.customer.address.locality.geo_skip))
        self.assertEquals(input.customer.address.locality.geo_diff, float(data.customer.address.locality.geo_diff))
        self.assertEquals(input.customer.address.street_id, default_address)
        self.assertEquals(input.customer.address.prefs, data.customer.address.prefs.split(','))
        self.assertEquals(input.customer.address.since, dt_parse(data.customer.address.since))
        self.assertEquals(input.customer.address.types, data.customer.address.types)
        self.assertIs(input.customer.address.opaque1, data.customer.address.opaque1)

# ################################################################################################################################
# ################################################################################################################################

    def test_top_level_skip_empty_true_no_force_empty_with_class(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', '-ccc', '-ddd'

                class SkipEmpty:
                    input = True

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        data = Bunch()
        data.aaa = 'aaa'
        data.bbb = 'bbb'

        input = MyService._sio.parse_input(data, DATA_FORMAT.JSON)
        self.assertIsInstance(input, Bunch)
        self.assertDictEqual(input, {
            'aaa': 'aaa',
            'bbb': 'bbb',
        })

# ################################################################################################################################
# ################################################################################################################################

