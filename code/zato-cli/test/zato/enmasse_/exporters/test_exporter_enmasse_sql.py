# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSQLExporter(TestCase):
    """ Tests exporting SQL connection pools to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.config_store = ConfigManager()
        self.config_store.load_yaml_string(template_complex_01)

# ################################################################################################################################

    def test_sql_export(self):

        import yaml
        template_dict = yaml.safe_load(template_complex_01)
        sql_list_from_yaml = template_dict.get('sql', [])

        exporter = EnmasseExporter(self.config_store)
        exported_data = exporter.export_to_dict()

        self.assertIn('sql', exported_data, 'Exporter did not produce an "sql" section.')
        exported_sql_list = exported_data['sql']

        self.assertEqual(len(exported_sql_list), len(sql_list_from_yaml),
            'Number of exported SQL connections does not match original YAML.')

        yaml_sql_by_name = {item['name']: item for item in sql_list_from_yaml}
        exported_sql_by_name = {item['name']: item for item in exported_sql_list}

        for name, yaml_def in yaml_sql_by_name.items():

            self.assertIn(name, exported_sql_by_name, f'SQL connection "{name}" from YAML not found in export.')
            exported_def = exported_sql_by_name[name]

            for field in ['name', 'type', 'host', 'port', 'db_name', 'username']:
                if field in yaml_def:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field),
                        f'Mismatch for "{field}" in SQL connection "{name}"')

            if 'extra' in yaml_def and yaml_def['extra']:
                self.assertIn('extra', exported_def, f'Missing "extra" field in SQL connection "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
