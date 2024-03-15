# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.api import Secret_Shadow
from zato.common.typing_ import cast_
from zato.common.util.config import replace_query_string_items

# Zato - Cython
from zato.simpleio import SecretConfig
from zato.simpleio import SIOServerConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class ConfigTestCase(TestCase):

    def test_replace_query_string_items(self):

        class _Server:
            sio_config = None

        # Prepare individual pieces of the secrets configuration
        exact = {'xApiKey', 'token'}
        prefixes = {'secret_prefix_', 'password_prefix_'}
        suffixes = {'_secret_suffix', '_password_suffix'}

        # Build the configuration of secrets first
        secret_config:'any_' = SecretConfig()
        secret_config.exact = exact
        secret_config.prefixes = prefixes
        secret_config.suffixes = suffixes

        sio_config:'any_' = SIOServerConfig()
        sio_config.secret_config = secret_config

        _server = cast_('ParallelServer', _Server())
        _server.sio_config = sio_config

        data01 = 'wss://hello?xApiKey=123'
        data02 = 'wss://hello?xApiKey=123&token=456'
        data03 = 'wss://hello?xApiKey=123&token=456&abc=111'
        data04 = 'wss://hello?abc=111&xApiKey=123&token=456&zxc=456'
        data05 = 'https://hello?secret_prefix_1=123&1_secret_suffix=456'
        data06 = 'https://hello?password_prefix_2=123&2_password_suffix=456'

        data01_expected = f'wss://hello?xApiKey={Secret_Shadow}'
        data02_expected = f'wss://hello?xApiKey={Secret_Shadow}&token={Secret_Shadow}'
        data03_expected = f'wss://hello?xApiKey={Secret_Shadow}&token={Secret_Shadow}&abc=111'
        data04_expected = f'wss://hello?abc=111&xApiKey={Secret_Shadow}&token={Secret_Shadow}&zxc=456'
        data05_expected = f'https://hello?secret_prefix_1={Secret_Shadow}&1_secret_suffix={Secret_Shadow}'
        data06_expected = f'https://hello?password_prefix_2={Secret_Shadow}&2_password_suffix={Secret_Shadow}'

        data01_replaced = replace_query_string_items(_server, data01)
        data02_replaced = replace_query_string_items(_server, data02)
        data03_replaced = replace_query_string_items(_server, data03)
        data04_replaced = replace_query_string_items(_server, data04)
        data05_replaced = replace_query_string_items(_server, data05)
        data06_replaced = replace_query_string_items(_server, data06)

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
