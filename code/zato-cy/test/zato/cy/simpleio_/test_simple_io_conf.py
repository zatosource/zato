# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common import simple_io_conf_contents
from zato.common.util import get_config_from_string

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

class SimpleIOConfig(BaseTestCase):

# ################################################################################################################################

    def test_default_config(self):
        config = get_config_from_string(simple_io_conf_contents)

        bool_        = config.bool
        int_         = config.int
        secret       = config.secret
        bytes_to_str = config.bytes_to_str
        default      = config.default

        self.assertEquals(bool_.exact, '')
        self.assertListEqual(bool_.prefix, ['by_', 'has_', 'is_', 'may_', 'needs_', 'should_'])
        self.assertEquals(bool_.suffix, '')

        self.assertEquals(int_.exact, 'id')
        self.assertEquals(int_.prefix, '')
        self.assertListEqual(int_.suffix, ['_count', '_id', '_size', '_size_min', '_size_max', '_timeout'])

        self.assertListEqual(secret.exact,
            ['auth_data', 'auth_token', 'password', 'password1', 'password2', 'secret_key', 'tls_pem_passphrase', 'token'])
        self.assertEquals(secret.prefix, '')
        self.assertEquals(secret.suffix, '')

        self.assertEquals(bytes_to_str.encoding, '{bytes_to_str_encoding}')

        self.assertEquals(default.default_value, '')
        self.assertEquals(default.default_input_value, '')
        self.assertEquals(default.default_output_value, '')
        self.assertEquals(default.response_elem, '')

        self.assertFalse(default.skip_empty_keys)
        self.assertFalse(default.skip_empty_request_keys)
        self.assertFalse(default.skip_empty_response_keys)

        self.assertEquals(default.input_required_name, 'input_required')
        self.assertEquals(default.input_optional_name, 'input_optional')
        self.assertEquals(default.output_required_name, 'output_required')
        self.assertEquals(default.output_optional_name, 'output_optional')

        self.assertEquals(default.prefix_as_is, 'a')
        self.assertEquals(default.prefix_bool, 'b')
        self.assertEquals(default.prefix_csv, 'c')
        self.assertEquals(default.prefix_date, 'date')
        self.assertEquals(default.prefix_date_time, 'dt')
        self.assertEquals(default.prefix_dict, 'd')
        self.assertEquals(default.prefix_dict_list, 'dl')
        self.assertEquals(default.prefix_float, 'f')
        self.assertEquals(default.prefix_int, 'i')
        self.assertEquals(default.prefix_list, 'l')
        self.assertEquals(default.prefix_text, 't')
        self.assertEquals(default.prefix_uuid, 'u')

# ################################################################################################################################
# ################################################################################################################################
