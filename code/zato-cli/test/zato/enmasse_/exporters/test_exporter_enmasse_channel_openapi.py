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
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelOpenAPIExporter(TestCase):
    """ Tests exporting OpenAPI channel definitions via ConfigStore round-trip.
    """

    def setUp(self) -> 'None':
        self.store = ConfigStore()
        self.store.load_yaml_string(template_complex_01)
        self.exported = self.store.export_to_dict()

# ################################################################################################################################

    def _find(self, items:'list', name:'str') -> 'dict':
        for item in items:
            if item.get('name') == name or item.get('security') == name:
                return item
        self.fail(f'Item not found -> {name}')

# ################################################################################################################################

    def test_channel_openapi_count(self) -> 'None':
        openapi_list = self.exported['channel_openapi']
        self.assertEqual(len(openapi_list), 2)

# ################################################################################################################################

    def test_channel_openapi_1(self) -> 'None':
        item = self._find(self.exported['channel_openapi'], 'enmasse.channel.openapi.1')
        self.assertEqual(item['rest_channel_list'], ['enmasse.channel.rest.1', 'enmasse.channel.rest.2'])

# ################################################################################################################################

    def test_channel_openapi_2(self) -> 'None':
        item = self._find(self.exported['channel_openapi'], 'enmasse.channel.openapi.2')
        self.assertEqual(item['name'], 'enmasse.channel.openapi.2')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
