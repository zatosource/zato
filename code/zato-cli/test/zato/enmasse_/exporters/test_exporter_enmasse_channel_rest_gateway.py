# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main
import yaml

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_rest_gateway import template_rest_gateway
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelRESTGatewayExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_rest_gateway)

    def test_rest_channel_gateway_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        if 'channel_rest' in exported_data:
            exported_channels = exported_data['channel_rest']
            for channel in exported_channels:
                if 'gateway_service_list' in channel:
                    self.assertIsInstance(channel['gateway_service_list'], list)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
