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

class TestEnmasseOutgoingRESTExporter(TestCase):
    """ Tests exporting outgoing REST connection definitions via ConfigStore round-trip.
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

    def test_outgoing_rest_count(self) -> 'None':
        outgoing_rest_list = self.exported['outgoing_rest']
        self.assertEqual(len(outgoing_rest_list), 5)

# ################################################################################################################################

    def test_outgoing_rest_1(self) -> 'None':
        item = self._find(self.exported['outgoing_rest'], 'enmasse.outgoing.rest.1')
        self.assertEqual(item['host'], 'https://example.com:443')
        self.assertEqual(item['url_path'], '/sso/{{type}}/hello/{{endpoint}}')
        self.assertEqual(item['data_format'], 'json')
        self.assertEqual(item['timeout'], 60)

# ################################################################################################################################

    def test_outgoing_rest_2(self) -> 'None':
        item = self._find(self.exported['outgoing_rest'], 'enmasse.outgoing.rest.2')
        self.assertEqual(item['host'], 'https://api.businesscentral.dynamics.com')
        self.assertEqual(item['url_path'], '/abc/2')
        self.assertEqual(item['security_name'], 'enmasse.bearer_token.1')
        self.assertEqual(item['timeout'], 20)

# ################################################################################################################################

    def test_outgoing_rest_3(self) -> 'None':
        item = self._find(self.exported['outgoing_rest'], 'enmasse.outgoing.rest.3')
        self.assertEqual(item['host'], 'https://example.azurewebsites.net')
        self.assertEqual(item['url_path'], '/abc/3')
        self.assertEqual(item['data_format'], 'json')

# ################################################################################################################################

    def test_outgoing_rest_4(self) -> 'None':
        item = self._find(self.exported['outgoing_rest'], 'enmasse.outgoing.rest.4')
        self.assertEqual(item['host'], 'https://example.com')
        self.assertEqual(item['url_path'], '/abc/4')
        self.assertEqual(item['ping_method'], 'GET')

# ################################################################################################################################

    def test_outgoing_rest_5(self) -> 'None':
        item = self._find(self.exported['outgoing_rest'], 'enmasse.outgoing.rest.5')
        self.assertEqual(item['host'], 'https://example.com')
        self.assertEqual(item['url_path'], '/abc/5')
        self.assertEqual(item['ping_method'], 'GET')
        self.assertEqual(item['tls_verify'], False)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
