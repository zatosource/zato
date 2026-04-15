# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main
import yaml

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato_server_core import ConfigStore

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOdooExporter(TestCase):

    def setUp(self) -> 'None':
        self.config_store = ConfigStore()
        self.config_store.load_yaml_string(template_complex_01)

    def test_odoo_export(self):

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('odoo', exported_data, 'Exporter did not produce an "odoo" section.')
        exported_list = exported_data['odoo']

        template_dict = yaml.safe_load(template_complex_01)
        yaml_list = template_dict.get('odoo', [])

        self.assertEqual(len(exported_list), len(yaml_list))

        exported_by_name = {item['name']: item for item in exported_list}

        for yaml_def in yaml_list:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name, f'Odoo "{name}" not found in export')
            exported_def = exported_by_name[name]
            for field in ['name', 'host', 'port', 'user', 'database']:
                self.assertEqual(exported_def.get(field), yaml_def.get(field),
                    f'Mismatch for "{field}" in Odoo "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
