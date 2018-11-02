# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Bunch
from bunch import Bunch, bunchify

# Zato
from zato.simpleio import BoolConfig, IntConfig, NotGiven, SecretConfig, SimpleIO, _SIOServerConfig

# ################################################################################################################################

class _Base(TestCase):
    def get_sio(self, declaration):

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

        sio = SimpleIO(SIOServerConfig, declaration)
        sio.build()

        return sio

# ################################################################################################################################

class InputOutputSyntaxParsing(_Base):

    def test_input_output_only(self):

        class SimpleIO:
            pass

        sio = self.get_sio(SimpleIO)

# ################################################################################################################################
