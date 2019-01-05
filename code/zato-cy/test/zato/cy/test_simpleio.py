# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from json import dumps, loads
from unittest import TestCase

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.common import DATA_FORMAT
from zato.server.service import Service
from zato.simpleio import AsIs, Bool, BoolConfig, CSV, CySimpleIO, Date, DateTime, Decimal, Dict, DictList, Float, Int, \
     IntConfig, List, NotGiven, Opaque, SecretConfig, _SIOServerConfig, Text, UUID

# Zato - Cython
from zato.util_convert import false_values, to_bool, true_values

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
        server_config.default.prefix_required = '+'
        server_config.default.prefix_optional = '-'

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
        SIOServerConfig.prefix_required = server_config.default.prefix_required
        SIOServerConfig.prefix_optional = server_config.default.prefix_optional

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

class FromJSONTestCase(_BaseTestCase):

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
        })

# ################################################################################################################################
# ################################################################################################################################
