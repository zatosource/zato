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

class TestEnmasseConfluenceImport(TestCase):

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

    def test_confluence_count(self) -> 'None':
        ldap_list = self.exported['ldap']
        confluence_items = [item for item in ldap_list if item.get('type_') == 'cloud-confluence']
        self.assertEqual(len(confluence_items), 1)

# ################################################################################################################################

    def test_confluence_1(self) -> 'None':
        ldap_list = self.exported['ldap']
        confluence_items = [item for item in ldap_list if item.get('type_') == 'cloud-confluence']
        item = self._find(confluence_items, 'enmasse.confluence.1')
        self.assertEqual(item['type_'], 'cloud-confluence')
        self.assertEqual(item['address'], 'https://example.atlassian.net')
        self.assertEqual(item['username'], 'api_user@example.com')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
