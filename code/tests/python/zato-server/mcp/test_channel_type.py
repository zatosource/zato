# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
import zato.server.base.config_manager as config_manager_module
from zato.bunch import Bunch
from zato.common.api import GENERIC as COMMON_GENERIC
from zato.server.generic.api.channel_mcp import ChannelMCPWrapper

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPConstant(TestCase):
    """ Tests that the CHANNEL_MCP constant is correctly defined.
    """

# ################################################################################################################################

    def test_constant_value(self):
        self.assertEqual(COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_MCP, 'channel-mcp')

# ################################################################################################################################

    def test_constant_is_string(self):
        self.assertIsInstance(COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_MCP, str)

# ################################################################################################################################
# ################################################################################################################################

class ChannelMCPWrapperInit(TestCase):
    """ Tests that the ChannelMCPWrapper can be instantiated and has the expected interface.
    """

# ################################################################################################################################

    def test_wrapper_stores_config_and_server(self):
        config = Bunch(name='test-mcp-channel')
        server = Bunch()

        wrapper = ChannelMCPWrapper(config, server)

        self.assertIs(wrapper.config, config)
        self.assertIs(wrapper.server, server)

# ################################################################################################################################

    def test_build_wrapper_callable(self):
        service_store = Bunch(services={}, name_to_impl_name={})
        config = Bunch(name='test-mcp-channel')
        server = Bunch(service_store=service_store)

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.build_wrapper()

# ################################################################################################################################

    def test_delete_callable(self):
        config = Bunch(name='test-mcp-channel')
        server = Bunch()

        wrapper = ChannelMCPWrapper(config, server)
        wrapper.delete()

# ################################################################################################################################
# ################################################################################################################################

class ConfigManagerGenericConnWiring(TestCase):
    """ Tests that ConfigManager maps include the CHANNEL_MCP type.
    """

# ################################################################################################################################

    def test_generic_conn_api_has_mcp(self):

        source = config_manager_module.__file__

        with open(source) as source_file:
            content = source_file.read()

        self.assertIn('CHANNEL_MCP', content)
        self.assertIn('self.channel_mcp', content)
        self.assertIn('ChannelMCPWrapper', content)

# ################################################################################################################################

    def test_wrapper_import(self):
        from zato.server.generic.api.channel_mcp import ChannelMCPWrapper as Imported
        self.assertIs(Imported, ChannelMCPWrapper)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
