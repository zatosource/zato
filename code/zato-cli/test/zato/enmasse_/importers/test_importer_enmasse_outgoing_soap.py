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

class TestEnmasseOutgoingSoapImport(TestCase):

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

    def test_outgoing_soap_count(self) -> 'None':
        soap_list = self.exported['outgoing_soap']
        self.assertEqual(len(soap_list), 1)

# ################################################################################################################################

    def test_outgoing_soap_1(self) -> 'None':
        item = self._find(self.exported['outgoing_soap'], 'enmasse.outgoing.soap.1')
        self.assertEqual(item['host'], 'https://example.com')
        self.assertEqual(item['url_path'], '/SOAP')
        self.assertEqual(item['security_name'], 'enmasse.ntlm.1')
        self.assertEqual(item['soap_action'], 'urn:microsoft-dynamics-schemas/page/example:Create')
        self.assertEqual(item['soap_version'], '1.1')
        self.assertFalse(item['tls_verify'])
        self.assertEqual(item['timeout'], 20)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
