# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# nose
from nose.tools import eq_

# Zato
from zato.common import DATA_FORMAT, NO_DEFAULT_VALUE, PARAMS_PRIORITY, SIMPLE_IO
from zato.common.test import rand_bool, rand_csv, rand_date_utc, rand_dict, rand_float, rand_int, rand_list, rand_list_of_dicts, \
     rand_nested, rand_opaque, rand_string, rand_unicode
from zato.common.util import new_cid
from zato.server.service.reqresp.sio import AsIs, Boolean, convert_param, CSV, Dict, Float, ForceType, Integer, List, \
     ListOfDicts, Nested, Opaque, Unicode, UTC, ValidationException

class SIOTestCase(TestCase):
    def test_dict_no_keys_specified(self):
        d = Dict('d')
        value = {rand_string(): rand_string(), rand_string(): rand_string()}

        ret_value = d.from_json(value)
        eq_(value, ret_value)

    def test_dict_keys_all_exist(self):
        d = Dict('d', 'k1', 'k2')
        value = {'k1':'v1', 'k2':'v2', 'k3':'v3'} # k3 is superfluous and should not be returned

        ret_value = d.from_json(value)
        eq_(sorted(ret_value.items()), [('k1', 'v1'), ('k2', 'v2')])

    def test_dict_keys_missing_no_default_value(self):
        d = Dict('d', 'k1', 'k2', 'k3', 'k4')
        value = {'k1':'v1', 'k2':'v2', 'k3':'v3'} # k4 doesn't exist so an exception should be raised

        try:
            d.from_json(value)
        except ValidationException, e:
            eq_(e.name, 'd')
            eq_(sorted(e.value.items()), [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')])
            eq_(e.missing_elem, 'k4')
        else:
            self.fail('Expected a ValidationException here')

    def test_dict_keys_missing_has_default_value(self):
        default = rand_string()
        d = Dict('d', 'k1', 'k2', 'k3', 'k4', default=default)
        value = {'k1':'v1', 'k2':'v2', 'k3':'v3'} # k4 doesn't exist but no exception is raised because a default value is set

        ret_value = d.from_json(value)
        eq_(sorted(ret_value.items()), [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3'), ('k4', default)])

    def test_nested_from_json(self):

        n = Nested('elem', 'sub1', Boolean('my_bool1'), 'sub2', 'sub3', Dict('my_dict1', 'key1', 'key2'))

        expected_sub1_1 = rand_string()
        expected_sub2_1 = rand_string()
        expected_sub3_1 = rand_string()
        expected_my_bool1_1 = rand_bool()
        expected_key1_1 = rand_string()
        expected_key2_1 = rand_string()

        value1 = {'elem': {
            'sub1': expected_sub1_1,
            'sub2': expected_sub2_1,
            'my_bool1': expected_my_bool1_1,
            'sub3': expected_sub3_1,
            'my_dict1' : {
                'key1': expected_key1_1,
                'key2': expected_key2_1,
            }
        }}

        ret_value = n.from_json(value1)

        eq_(ret_value,
            {'elem':
             {'my_bool1': expected_my_bool1_1, 'sub2': expected_sub2_1, 'sub3': expected_sub3_1,
              'my_dict1': {'key2': expected_key2_1, 'key1': expected_key1_1},
              'sub1': expected_sub1_1}}
        )

    def test_nested_to_json(self):

        n = Nested('elem', 'sub1', Boolean('my_bool1'), 'sub2', 'sub3', Dict('my_dict1', 'key1', 'key2'))

        expected_sub1_2 = rand_string()
        expected_sub2_2 = rand_string()
        expected_sub3_2 = rand_string()
        expected_my_bool1_2 = rand_bool()
        expected_key1_2 = rand_string()
        expected_key2_2 = rand_string()

        value2 = {'elem': {
            'sub1': expected_sub1_2,
            'sub2': expected_sub2_2,
            'my_bool1': expected_my_bool1_2,
            'sub3': expected_sub3_2,
            'my_dict1' : {
                'key1': expected_key1_2,
                'key2': expected_key2_2,
            }
        }}

        ret_value = n.to_json(value2)

        eq_(ret_value,
            {'elem':
             {'my_bool1': expected_my_bool1_2, 'sub2': expected_sub2_2, 'sub3': expected_sub3_2,
              'my_dict1': {'key2': expected_key2_2, 'key1': expected_key1_2},
              'sub1': expected_sub1_2}}
        )

class ConvertParamTestCase(TestCase):

    def get_args(self, cid=None, payload=None, param=None, data_format=None, is_required=None, default_value=None,
            path_prefix=None, use_text=None, channel_params=None, has_simple_io_config=None, bool_parameter_prefixes=None,
            int_parameters=None, int_parameter_suffixes=None, params_priority=None):

        return {
            'cid': cid or new_cid(),
            'payload': payload if payload is not None else {'a':'1'},
            'param': param or Integer('a'),
            'data_format': data_format or DATA_FORMAT.JSON,
            'is_required': is_required or True,
            'default_value': default_value or NO_DEFAULT_VALUE,
            'path_prefix': path_prefix or 'request',
            'use_text': use_text or True,
            'channel_params': channel_params or {},
            'has_simple_io_config': has_simple_io_config or True,
            'bool_parameter_prefixes': bool_parameter_prefixes or SIMPLE_IO.BOOL_PARAMETERS.SUFFIXES,
            'int_parameters': int_parameters or SIMPLE_IO.INT_PARAMETERS.VALUES,
            'int_parameter_suffixes': int_parameter_suffixes or SIMPLE_IO.INT_PARAMETERS.SUFFIXES,
            'params_priority': params_priority or PARAMS_PRIORITY.MSG_OVER_CHANNEL_PARAMS,
        }

# ################################################################################################################################

    def test_convert_int_payload_json_req_from_string(self):

        # Equivalent to
        #
        # POST /foo
        # {'item':'1'}
        #
        # Where 'item' is a required element.

        param_name = rand_string()
        value = str(rand_int())
        args = self.get_args(param=Integer(param_name), payload={param_name:value})

        given_param_name, given_value = convert_param(**args)

        self.assertEquals(param_name, given_param_name)
        self.assertEquals(int(value), given_value)

    def test_convert_int_payload_json_req_from_int(self):

        # Equivalent to
        #
        # POST /foo
        # {'item':1}
        #
        # Where 'item' is a required element.

        param_name = rand_string()
        value = rand_int()
        args = self.get_args(param=Integer(param_name), payload={param_name:value})

        given_param_name, given_value = convert_param(**args)

        self.assertEquals(param_name, given_param_name)
        self.assertEquals(value, given_value)

    def test_convert_int_url_params_from_string(self):

        # Equivalent to
        #
        # GET /foo?item=1
        #
        # Where 'item' is a required element (as string in channel_params).

        param_name = rand_string()
        value = str(rand_int())
        args = self.get_args(param=Integer(param_name), channel_params={param_name:value}, payload='')

        given_param_name, given_value = convert_param(**args)

        self.assertEquals(param_name, given_param_name)
        self.assertEquals(int(value), given_value)

    def test_convert_int_url_params_from_int(self):

        # Equivalent to
        #
        # GET /foo?item=1
        #
        # Where 'item' is a required element (as int in channel_params).

        param_name = rand_string()
        value = rand_int()
        args = self.get_args(param=Integer(param_name), channel_params={param_name:value}, payload='')

        given_param_name, given_value = convert_param(**args)

        self.assertEquals(param_name, given_param_name)
        self.assertEquals(value, given_value)

    def test_convert_sio_types(self):

        def _rand_date_utc():
            return rand_date_utc(True)

        func_to_type = {
            rand_bool: Boolean,
            rand_csv: CSV,
            _rand_date_utc: UTC,
            rand_dict: Dict,
            rand_float: Float,
            rand_int: Integer,
            rand_list: List,
            rand_list_of_dicts: ListOfDicts,
            rand_nested: Nested,
            rand_opaque: Opaque,
            rand_string: str,
            rand_unicode: Unicode
        }

        for func, type_ in func_to_type.items():

            for use_payload in (True, False):

                param_name = rand_string()
                payload_value = func()
                channel_value = func()

                if use_payload:
                    channel_params = {}
                    payload = {param_name:payload_value}
                    expected_value = payload_value
                else:
                    channel_params = {param_name:channel_value}
                    payload = {}
                    expected_value = channel_value

                if type_ is CSV:
                    expected_value = [elem.strip() for elem in expected_value.split(',')]

                test_func = self.assertIs if type_ in (Opaque, Nested) else self.assertEquals
                args = self.get_args(param=type_(param_name), channel_params=channel_params, payload=payload)
                given_param_name, given_value = convert_param(**args)

                self.assertEquals(param_name, given_param_name)
                test_func(expected_value, given_value, '{!r} != {!r} {} {} {}'.format(
                    expected_value, given_value, func, type_, test_func))

                del expected_value, payload_value, channel_value

# ################################################################################################################################

    def test_convert_check_priority(self):

        func_to_type = {
            rand_bool: Boolean,
            rand_float: Float,
            rand_int: Integer,
            rand_string: str,
        }

        for func, type_ in func_to_type.items():
            for params_priority in PARAMS_PRIORITY:

                param_name = rand_string()
                payload_value = func()
                channel_value = func()

                args = self.get_args(param=type_(param_name), channel_params={param_name:channel_value},
                    payload={param_name:payload_value}, params_priority=params_priority)

                given_param_name, given_value = convert_param(**args)
                expected_value = channel_value if params_priority == PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG else payload_value

                self.assertEquals(param_name, given_param_name)
                self.assertEquals(expected_value, given_value)

# ################################################################################################################################
