# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.common.test.enmasse_._template_complex_01 import template_complex_01

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelRestImport(TestCase):

    def setUp(self) -> 'None':
        self.store = ConfigStore()
        self.store.load_yaml_string(template_complex_01)
        self.exported = self.store.export_to_dict()

# ################################################################################################################################

    def _find(self, items:'list', name:'str') -> 'dict':
        for item in items:
            if item.get('name') == name:
                return item
        self.fail(f'Item not found -> {name}')

# ################################################################################################################################

    def test_channel_rest_count(self) -> 'None':
        channel_list = self.exported['channel_rest']
        self.assertEqual(len(channel_list), 4)

# ################################################################################################################################

    def test_channel_rest_1(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.1')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['url_path'], '/enmasse.rest.1')
        self.assertIsNone(item.get('data_format'))

# ################################################################################################################################

    def test_channel_rest_2(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.2')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['url_path'], '/enmasse.rest.2')
        self.assertEqual(item['data_format'], 'json')

# ################################################################################################################################

    def test_channel_rest_3(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.3')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['url_path'], '/enmasse.rest.3')
        self.assertEqual(item['data_format'], 'json')
        self.assertEqual(item['security_name'], 'enmasse.basic_auth.1')

# ################################################################################################################################

    def test_channel_rest_4(self) -> 'None':
        item = self._find(self.exported['channel_rest'], 'enmasse.channel.rest.4')
        self.assertEqual(item['service'], 'demo.ping')
        self.assertEqual(item['url_path'], '/enmasse.rest.4')
        self.assertEqual(item['data_format'], 'json')
        self.assertEqual(sorted(item['groups']), ['enmasse.group.1', 'enmasse.group.2'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
