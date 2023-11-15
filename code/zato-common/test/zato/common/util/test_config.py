# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.api import Secret_Shadow
from zato.common.util.config import replace_query_string_items

# Zato - Cython
from zato.simpleio import SecretConfig
from zato.simpleio import SIOServerConfig

# ################################################################################################################################
# ################################################################################################################################

class ConfigTestCase(TestCase):

    def test_replace_query_string_items(self):

        # Prepare individual pieces of the secrets configuration
        exact = {'xApiKey', 'token'}
        prefixes = {'secret_prefix_', 'password_prefix_'}
        suffixes = {'_secret_suffix', '_password_suffix'}

        # Build the configuration of secrets first
        secret_config = SecretConfig()
        secret_config.exact = exact
        secret_config.prefixes = prefixes
        secret_config.suffixes = suffixes

        sio_config = SIOServerConfig()
        sio_config.secret_config = secret_config

        data01 = 'wss://hello?xApiKey=123'
        data02 = 'wss://hello?xApiKey=123&token=456'
        data03 = 'wss://hello?xApiKey=123&token=456&abc=111'
        data04 = 'wss://hello?abc=111xApiKey=123&token=456&zxc=456'
        data05 = 'https://hello?secret_prefix_1=123&password_prefix_2=456'
        data06 = 'https://hello?secret_prefix_1=123&password_prefix_2=456'

        data01_expected = f'wss://hello?xApiKey={Secret_Shadow}'
        data02_expected = f'wss://hello?xApiKey={Secret_Shadow}&token={Secret_Shadow}'
        data03_expected = f'wss://hello?xApiKey={Secret_Shadow}&token={Secret_Shadow}&abc=111'
        data04_expected = f'wss://hello?abc=111xApiKey={Secret_Shadow}&token={Secret_Shadow}&zxc=456'
        data05_expected = f'https://hello?secret_prefix_1={Secret_Shadow}&password_prefix_2={Secret_Shadow}'
        data06_expected = f'https://hello?secret_prefix_1={Secret_Shadow}&password_prefix_2={Secret_Shadow}'

        data01_replaced = replace_query_string_items(sio_config, data01)
        data02_replaced = replace_query_string_items(sio_config, data02)
        data03_replaced = replace_query_string_items(sio_config, data03)
        data04_replaced = replace_query_string_items(sio_config, data04)
        data05_replaced = replace_query_string_items(sio_config, data05)
        data06_replaced = replace_query_string_items(sio_config, data06)

        self.assertEqual(data01_replaced, data01_expected)
        self.assertEqual(data02_replaced, data02_expected)
        self.assertEqual(data03_replaced, data03_expected)
        self.assertEqual(data04_replaced, data04_expected)
        self.assertEqual(data05_replaced, data05_expected)
        self.assertEqual(data06_replaced, data06_expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
