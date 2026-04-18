# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOdooImport(TestCase):

    def setUp(self) -> 'None':
        self.config_manager = ConfigManager()
        self.importer = EnmasseImporter(self.config_manager)
        self.importer.import_(template_complex_01)

# ################################################################################################################################

    def test_odoo_preprocessing_defaults(self):

        template_dict = yaml.safe_load(template_complex_01)
        odoo_items = template_dict['odoo']

        preprocessed = OdooImporter.preprocess(odoo_items)

        for item in preprocessed:
            self.assertIn('password', item)
            self.assertEqual(item.get('protocol'), 'jsonrpc')

# ################################################################################################################################

    def test_odoo_imported(self):

        exported = self.config_manager.export_to_dict()
        self.assertIn('odoo', exported)

        odoo_list = exported['odoo']
        odoo_by_name = {item['name']: item for item in odoo_list}
        self.assertIn('enmasse.odoo.1', odoo_by_name)

# ################################################################################################################################

    def test_odoo_values(self):

        exported = self.config_manager.export_to_dict()
        odoo_list = exported['odoo']
        odoo_by_name = {item['name']: item for item in odoo_list}

        o1 = odoo_by_name['enmasse.odoo.1']
        self.assertEqual(o1['host'], 'odoo.example.com')
        self.assertEqual(o1['port'], 8069)
        self.assertEqual(o1['database'], 'enmasse_db')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
