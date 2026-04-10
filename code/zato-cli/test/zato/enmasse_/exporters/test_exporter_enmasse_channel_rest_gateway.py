# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.common.test.enmasse_._template_rest_gateway import template_rest_gateway

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelRESTGatewayExporter(TestCase):
    """ Tests exporting REST channels with gateway_service_list via ConfigStore round-trip.
    """

    def setUp(self) -> 'None':
        self.store = ConfigStore()
        self.store.load_yaml_string(template_rest_gateway)
        self.exported = self.store.export_to_dict()

# ################################################################################################################################

    def _find(self, items:'list', name:'str') -> 'dict':
        for item in items:
            if item.get('name') == name or item.get('security') == name:
                return item
        self.fail(f'Item not found -> {name}')

# ################################################################################################################################

    def test_gateway_channel_1(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.gateway.1')
        self.assertEqual(item['gateway_service_list'], ['demo.ping', 'api.my-service'])

# ################################################################################################################################

    def test_gateway_channel_2_no_gateway(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.gateway.2')
        self.assertEqual(item['gateway_service_list'], [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
