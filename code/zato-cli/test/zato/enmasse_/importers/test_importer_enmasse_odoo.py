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

class TestEnmasseOdooImport(TestCase):

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

    def test_odoo_count(self) -> 'None':
        odoo_list = self.exported['odoo']
        self.assertEqual(len(odoo_list), 1)

# ################################################################################################################################

    def test_odoo_1(self) -> 'None':
        item = self._find(self.exported['odoo'], 'enmasse.odoo.1')
        self.assertEqual(item['host'], 'odoo.example.com')
        self.assertEqual(item['port'], 8069)
        self.assertEqual(item['user'], 'admin')
        self.assertEqual(item['database'], 'enmasse_db')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
