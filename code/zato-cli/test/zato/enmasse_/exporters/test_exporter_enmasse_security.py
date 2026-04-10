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

class TestEnmasseSecurityExporter(TestCase):
    """ Tests exporting security definitions via ConfigStore round-trip.
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

    def test_security_count(self) -> 'None':
        security_list = self.exported['security']
        self.assertEqual(len(security_list), 8)

# ################################################################################################################################

    def test_security_basic_auth_1(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.basic_auth.1')
        self.assertEqual(item['type'], 'basic_auth')
        self.assertEqual(item['name'], 'enmasse.basic_auth.1')

# ################################################################################################################################

    def test_security_basic_auth_2(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.basic_auth.2')
        self.assertEqual(item['type'], 'basic_auth')

# ################################################################################################################################

    def test_security_basic_auth_3(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.basic_auth.3')
        self.assertEqual(item['type'], 'basic_auth')

# ################################################################################################################################

    def test_security_bearer_token_1(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.bearer_token.1')
        self.assertEqual(item['type'], 'bearer_token')

# ################################################################################################################################

    def test_security_bearer_token_2(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.bearer_token.2')
        self.assertEqual(item['type'], 'bearer_token')

# ################################################################################################################################

    def test_security_ntlm(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.ntlm.1')
        self.assertEqual(item['type'], 'ntlm')

# ################################################################################################################################

    def test_security_apikey_1(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.apikey.1')
        self.assertEqual(item['type'], 'apikey')

# ################################################################################################################################

    def test_security_apikey_2(self) -> 'None':
        item = self._find(self.exported['security'], 'enmasse.apikey.2')
        self.assertEqual(item['type'], 'apikey')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
