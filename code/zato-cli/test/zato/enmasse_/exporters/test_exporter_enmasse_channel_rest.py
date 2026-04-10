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

class TestEnmasseChannelRESTExporter(TestCase):
    """ Tests exporting REST channel definitions via ConfigStore round-trip.
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

    def test_channel_rest_count(self) -> 'None':
        channel_rest_list = self.exported['channel_rest']
        self.assertEqual(len(channel_rest_list), 4)

# ################################################################################################################################

    def test_channel_rest_1(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.1')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['url_path'], '/enmasse.rest.1')

# ################################################################################################################################

    def test_channel_rest_2(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.2')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['url_path'], '/enmasse.rest.2')
        self.assertEqual(item['data_format'], 'json')

# ################################################################################################################################

    def test_channel_rest_3_security_name(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.3')
        self.assertEqual(item['security_name'], 'enmasse.basic_auth.1')
        self.assertEqual(item['data_format'], 'json')

# ################################################################################################################################

    def test_channel_rest_4_groups(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.4')
        self.assertEqual(item['data_format'], 'json')
        self.assertIn('enmasse.group.1', item['groups'])
        self.assertIn('enmasse.group.2', item['groups'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
